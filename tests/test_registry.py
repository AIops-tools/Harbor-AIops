"""Harbor API contract tests based on the upstream v2.0 Swagger paths and paging."""

import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

from harbor_aiops.config import TargetConfig
from harbor_aiops.connection import HarborApiError, HarborConnection
from harbor_aiops.ops import registry, writes


def _connection(handler):
    client = httpx.Client(
        base_url="https://harbor.test/api/v2.0/",
        auth=httpx.BasicAuth("robot$test", "secret"),
        transport=httpx.MockTransport(handler),
    )
    return HarborConnection(TargetConfig("lab", "harbor.test", "robot$test"), client)


def test_gc_pagination_reads_extra_item_without_skipping_page():
    seen = []

    def handler(request):
        assert request.url.path == "/api/v2.0/system/gc"
        assert request.headers["Authorization"].startswith("Basic ")
        page = int(request.url.params["page"])
        size = int(request.url.params["page_size"])
        seen.append((page, size))
        all_rows = [{"id": i, "status": "Success"} for i in range(101)]
        start = (page - 1) * size
        return httpx.Response(200, json=all_rows[start : start + size])

    result = registry.gc_history(_connection(handler), limit=100)
    assert result["returned"] == 100
    assert result["truncated"] is True
    assert result["items"][0]["id"] == 0
    assert result["items"][-1]["id"] == 99
    assert seen == [(1, 100), (2, 100)]


def test_exact_limit_probes_following_page():
    def handler(request):
        page = int(request.url.params["page"])
        return httpx.Response(200, json=[{"id": 1}] if page == 1 else [])

    result = registry.gc_history(_connection(handler), limit=1)
    assert result == {"items": [{"id": 1}], "returned": 1, "limit": 1, "truncated": False}


def test_permission_failure_is_not_an_empty_gc_history():
    def handler(request):
        return httpx.Response(403, json={"errors": [{"message": "forbidden"}]})

    with pytest.raises(HarborApiError, match="lacks permission"):
        registry.gc_history(_connection(handler))


def test_unknown_path_fails_loudly_and_diagnosis_reports_partial_failure():
    def handler(request):
        if request.url.path == "/api/v2.0/health":
            return httpx.Response(200, json={"status": "healthy", "components": []})
        if request.url.path == "/api/v2.0/systeminfo/volumes":
            return httpx.Response(403, json={})
        if request.url.path == "/api/v2.0/system/gc":
            return httpx.Response(200, json=[])
        if request.url.path == "/api/v2.0/replication/executions":
            return httpx.Response(200, json=[])
        raise AssertionError(f"Unexpected Harbor path {request.url.path}")

    result = registry.diagnosis(_connection(handler))
    assert result["complete"] is False
    assert result["failedProbes"] == ["volumes"]
    assert result["probes"]["volumes"]["data"] is None
    assert "403" in result["probes"]["volumes"]["error"]


def test_retention_id_is_validated_before_request():
    conn = _connection(lambda request: (_ for _ in ()).throw(AssertionError("unexpected request")))
    with pytest.raises(ValueError, match="positive"):
        registry.retention_policy(conn, -1)


def test_slash_in_repository_name_is_encoded_twice_and_failed_probe_is_not_empty():
    def handler(request):
        assert request.url.raw_path.startswith(
            b"/api/v2.0/projects/ops/repositories/team%252Fapp/artifacts"
        )
        if request.url.path.endswith("/tags"):
            return httpx.Response(403, json={"errors": [{"message": "forbidden"}]})
        return httpx.Response(200, json=[{"digest": "sha256:abc"}])

    conn = _connection(handler)
    rows = registry.artifacts(conn, "ops", "team/app")
    assert rows["returned"] == 1 and rows["truncated"] is False
    with pytest.raises(HarborApiError, match="lacks permission"):
        registry.tags(conn, "ops", "team/app", "sha256:abc")


def test_project_path_segment_rejects_slash():
    conn = _connection(lambda request: (_ for _ in ()).throw(AssertionError("unexpected")))
    with pytest.raises(ValueError, match="segment"):
        registry.project(conn, "ops/other")


def test_tag_creation_previews_without_write_then_verifies_real_tag():
    posted = []

    def handler(request):
        path = request.url.path
        raw_path = request.url.raw_path.decode()
        assert "team%252Fapp" in raw_path
        if request.method == "GET" and path.endswith("/artifacts/v1"):
            return httpx.Response(200, json={"digest": "sha256:abc"})
        if request.method == "GET" and path.endswith("/artifacts/sha256:abc/tags"):
            assert request.url.params["page"] == "1"
            return httpx.Response(200, json=[{"name": "stable"}] if posted else [])
        if request.method == "POST" and path.endswith("/artifacts/sha256:abc/tags"):
            posted.append(request.content)
            return httpx.Response(201, headers={"X-Request-Id": "req-1"})
        raise AssertionError(f"Unexpected {request.method} {path}")

    conn = _connection(handler)
    preview = writes.create_tag(conn, "ops", "team/app", "v1", "stable", dry_run=True)
    assert preview["dryRun"] is True and posted == []
    result = writes.create_tag(conn, "ops", "team/app", "v1", "stable")
    assert result["created"] is True and result["artifactDigest"] == "sha256:abc"
    assert posted == [b'{"name":"stable"}']


def test_scan_acceptance_is_not_completion():
    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json={"digest": "sha256:abc"})
        assert request.method == "POST" and request.url.path.endswith("/scan")
        return httpx.Response(202)

    result = writes.scan_artifact(_connection(handler), "ops", "app", "v1")
    assert result["accepted"] is True and result["outcomeUnknown"] is True


def test_plain_text_gc_log_is_bounded_and_rejects_permission_failure():
    def handler(request):
        assert request.url.path == "/api/v2.0/system/gc/7/log"
        return httpx.Response(200, text="x" * 30)

    result = _connection(handler).get_text("/system/gc/7/log", max_bytes=10)
    assert result == {"text": "x" * 10 + "…", "truncated": True}
    denied = _connection(lambda request: httpx.Response(403, text="forbidden"))
    with pytest.raises(HarborApiError, match="403"):
        registry.gc_log(denied, 7)


def test_post_response_loss_is_unknown_and_server_rejection_is_error(monkeypatch, tmp_path):
    from harbor_aiops.governance.audit import reset_engine
    from harbor_aiops.mcp_server.tools import writes as tools

    mode = "timeout"

    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json={"digest": "sha256:abc"})
        if mode == "rejected":
            return httpx.Response(403)
        if mode == "server-error":
            return httpx.Response(500)
        if mode == "redirect":
            return httpx.Response(302, headers={"Location": "/login"})
        raise httpx.ReadTimeout("response lost")

    conn = _connection(handler)
    monkeypatch.setattr(tools, "_get_connection", lambda target=None: conn)
    monkeypatch.setenv("HARBOR_AIOPS_HOME", str(tmp_path))
    reset_engine()
    try:
        assert tools.harbor_scan_artifact("ops", "app", "v1")["outcomeUnknown"] is True
        mode = "server-error"
        assert tools.harbor_scan_artifact("ops", "app", "v1")["outcomeUnknown"] is True
        mode = "redirect"
        redirected = tools.harbor_scan_artifact("ops", "app", "v1")
        assert "302" in redirected["error"] and "outcomeUnknown" not in redirected
        mode = "rejected"
        failed = tools.harbor_scan_artifact("ops", "app", "v1")
        assert "403" in failed["error"] and "outcomeUnknown" not in failed
    finally:
        reset_engine()


def test_mcp_surface_has_governed_inventory_and_diagnosis():
    from harbor_aiops.mcp_server.server import mcp

    listed = asyncio.run(mcp.list_tools())
    assert len(listed) == 39
    assert {t.name for t in listed} >= {"harbor_gc_history", "harbor_replication_tasks",
                                             "harbor_retention_executions", "harbor_diagnose"}
    writes = {"undo_apply", "harbor_scan_artifact", "harbor_create_tag",
              "harbor_delete_tag"}
    assert all(t.annotations.read_only_hint for t in listed if t.name not in writes)
    assert all(not t.annotations.read_only_hint for t in listed if t.name in writes)


def test_delete_tag_previews_then_deletes_exact_mutable_tag_with_post_read():
    deleted = []

    def handler(request):
        path = request.url.path
        assert b"team%252Fapp" in request.url.raw_path
        if request.method == "GET" and path.endswith("/artifacts/v1"):
            return httpx.Response(200, json={"digest": "sha256:abc"})
        if request.method == "GET" and path.endswith("/artifacts/stable"):
            return (httpx.Response(404) if deleted else
                    httpx.Response(200, json={"digest": "sha256:abc"}))
        if request.method == "GET" and path.endswith("/artifacts/sha256:abc/tags"):
            return httpx.Response(200, json=[{"name": "stable", "immutable": False}])
        if request.method == "DELETE" and path.endswith(
            "/artifacts/sha256:abc/tags/stable"
        ):
            deleted.append(path)
            return httpx.Response(200)
        raise AssertionError(f"Unexpected {request.method} {path}")

    conn = _connection(handler)
    preview = writes.delete_tag(conn, "ops", "team/app", "v1", "stable", dry_run=True)
    assert preview["dryRun"] is True and deleted == []
    result = writes.delete_tag(conn, "ops", "team/app", "v1", "stable")
    assert result["deleted"] is True and len(deleted) == 1


@pytest.mark.parametrize("immutable", [True, None])
def test_delete_tag_refuses_immutable_or_unknown_state_without_write(immutable):
    def handler(request):
        path = request.url.path
        if request.method == "DELETE":
            raise AssertionError("delete must not run")
        if path == "/api/v2.0/projects/ops/repositories/app/artifacts/sha256:abc/tags":
            return httpx.Response(200, json=[{"name": "stable", "immutable": immutable}])
        if path in (
            "/api/v2.0/projects/ops/repositories/app/artifacts/v1",
            "/api/v2.0/projects/ops/repositories/app/artifacts/stable",
        ):
            return httpx.Response(200, json={"digest": "sha256:abc"})
        raise AssertionError(f"Unexpected {request.method} {path}")

    with pytest.raises(ValueError, match="immutability"):
        writes.delete_tag(_connection(handler), "ops", "app", "v1", "stable")


def test_delete_tag_post_read_failure_is_unknown_not_success():
    deleted = []

    def handler(request):
        path = request.url.path
        if request.method == "DELETE":
            assert path == (
                "/api/v2.0/projects/ops/repositories/app/"
                "artifacts/sha256:abc/tags/stable"
            )
            deleted.append(1)
            return httpx.Response(200)
        if path == "/api/v2.0/projects/ops/repositories/app/artifacts/sha256:abc/tags":
            return httpx.Response(200, json=[{"name": "stable", "immutable": False}])
        if path == "/api/v2.0/projects/ops/repositories/app/artifacts/stable" and deleted:
            return httpx.Response(503)
        if path in (
            "/api/v2.0/projects/ops/repositories/app/artifacts/v1",
            "/api/v2.0/projects/ops/repositories/app/artifacts/stable",
        ):
            return httpx.Response(200, json={"digest": "sha256:abc"})
        raise AssertionError(f"Unexpected {request.method} {path}")

    result = writes.delete_tag(_connection(handler), "ops", "app", "v1", "stable")
    assert result["outcomeUnknown"] is True and "deleted" not in result


def test_new_registry_reads_use_swagger_paths_and_redact_robot_secret():
    seen = []

    def handler(request):
        path = request.url.path
        seen.append((path, dict(request.url.params)))
        if path == "/api/v2.0/statistics":
            return httpx.Response(200, json={"total_project_count": 2})
        if path == "/api/v2.0/projects/ops/members":
            return httpx.Response(200, json=[{"entity_name": "alice"}])
        if path == "/api/v2.0/projects/ops/immutabletagrules":
            return httpx.Response(200, json=[{"id": 7}])
        if path == "/api/v2.0/robots":
            return httpx.Response(200, json=[{"name": "bot", "secret": "sensitive"}])
        if path == "/api/v2.0/labels":
            return httpx.Response(200, json=[{"name": "prod"}])
        if path in ("/api/v2.0/scans/all/metrics", "/api/v2.0/scans/schedule/metrics"):
            return httpx.Response(200, json={"status": "finished"})
        if path.endswith("/scan/report-7/log"):
            assert b"team%252Fapp" in request.url.raw_path
            return httpx.Response(200, text="scan complete")
        raise AssertionError(f"Unexpected {path}")

    conn = _connection(handler)
    assert registry.statistics(conn)["total_project_count"] == 2
    assert registry.project_members(conn, "ops", 1)["items"][0]["entity_name"] == "alice"
    assert registry.immutable_rules(conn, "ops", 1)["returned"] == 1
    assert registry.robot_accounts(conn, 1)["items"] == [
        {"name": "bot", "secret": "[REDACTED]"}
    ]
    assert registry.labels(conn, 1)["returned"] == 1
    assert registry.scan_metrics(conn)["status"] == "finished"
    assert registry.scan_metrics(conn, scheduled=True)["status"] == "finished"
    assert registry.scan_log(conn, "ops", "team/app", "v1", "report-7") == {
        "text": "scan complete", "truncated": False,
    }
    assert any(query.get("page_size") == "2" for _, query in seen)


def test_robot_account_permission_failure_and_bad_shape_are_not_empty():
    denied = _connection(lambda request: httpx.Response(403, json={}))
    with pytest.raises(HarborApiError, match="permission"):
        registry.robot_accounts(denied)
    bad = _connection(lambda request: httpx.Response(200, json=["not an object"]))
    with pytest.raises(ValueError, match="non-object"):
        registry.robot_accounts(bad)


def test_loopback_harbor_client_does_not_send_basic_auth_to_environment_proxy(
    monkeypatch, tmp_path
):
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append((self.path, self.headers.get("Authorization")))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"healthy"}')

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("HARBOR_LAB_PASSWORD", "secret")
    monkeypatch.setenv("HARBOR_AIOPS_HOME", str(tmp_path))
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:1")
    monkeypatch.setenv("ALL_PROXY", "http://127.0.0.1:1")
    monkeypatch.setenv("NO_PROXY", "")
    try:
        target = TargetConfig("lab", "127.0.0.1", "robot$test", scheme="http",
                              port=server.server_port)
        conn = HarborConnection(target)
        assert registry.health(conn)["status"] == "healthy"
        conn.close()
        assert seen[0][0] == "/api/v2.0/health"
        assert seen[0][1].startswith("Basic ")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
