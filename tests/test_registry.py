"""Harbor API contract tests based on the upstream v2.0 Swagger paths and paging."""

import asyncio

import httpx
import pytest

from harbor_aiops.config import TargetConfig
from harbor_aiops.connection import HarborApiError, HarborConnection
from harbor_aiops.ops import registry


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


def test_mcp_surface_is_ten_governed_tools():
    from harbor_aiops.mcp_server.server import mcp

    listed = asyncio.run(mcp.list_tools())
    assert len(listed) == 10
    assert {t.name for t in listed} >= {"harbor_gc_history", "harbor_replication_tasks",
                                             "harbor_retention_executions", "harbor_diagnose"}
    assert all(t.annotations.read_only_hint for t in listed if t.name != "undo_apply")
