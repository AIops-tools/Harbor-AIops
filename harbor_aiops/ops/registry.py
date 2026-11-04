"""Read-only Harbor registry operation and incident views."""

from __future__ import annotations

from typing import Any

from harbor_aiops.connection import HarborConnection, repository_segment, segment


def _artifact_path(project: str, repository: str, reference: str | None = None) -> str:
    path = f"/projects/{segment(project)}/repositories/{repository_segment(repository)}/artifacts"
    return path if reference is None else f"{path}/{segment(reference)}"


def projects(conn: HarborConnection, limit: int = 50) -> dict:
    return conn.list("/projects", limit=limit)


def project(conn: HarborConnection, name: str) -> dict:
    value = conn.get(f"/projects/{segment(name)}")
    if not isinstance(value, dict):
        raise ValueError("Harbor project response was not an object.")
    return value


def project_summary(conn: HarborConnection, name: str) -> dict:
    value = conn.get(f"/projects/{segment(name)}/summary")
    if not isinstance(value, dict):
        raise ValueError("Harbor project summary response was not an object.")
    return value


def repositories(conn: HarborConnection, project_name: str, limit: int = 50) -> dict:
    return conn.list(f"/projects/{segment(project_name)}/repositories", limit=limit)


def artifacts(
    conn: HarborConnection, project_name: str, repository_name: str, limit: int = 50
) -> dict:
    return conn.list(
        _artifact_path(project_name, repository_name), limit=limit,
        params={"with_tag": "true", "with_scan_overview": "true"},
    )


def artifact(
    conn: HarborConnection, project_name: str, repository_name: str, reference: str
) -> dict:
    value = conn.get(
        _artifact_path(project_name, repository_name, reference),
        {"with_tag": "true", "with_scan_overview": "true", "with_immutable_status": "true"},
    )
    if not isinstance(value, dict):
        raise ValueError("Harbor artifact response was not an object.")
    return value


def tags(
    conn: HarborConnection, project_name: str, repository_name: str, reference: str,
    limit: int = 50,
) -> dict:
    return conn.list(
        _artifact_path(project_name, repository_name, reference) + "/tags",
        limit=limit, params={"with_immutable_status": "true"},
    )


def vulnerabilities(
    conn: HarborConnection, project_name: str, repository_name: str, reference: str
) -> dict:
    value = conn.get(
        _artifact_path(project_name, repository_name, reference)
        + "/additions/vulnerabilities"
    )
    if not isinstance(value, dict):
        raise ValueError("Harbor vulnerability report was not an object.")
    return value


def replication_policies(conn: HarborConnection, limit: int = 50) -> dict:
    return conn.list("/replication/policies", limit=limit)


def replication_policy(conn: HarborConnection, policy_id: int) -> dict:
    if policy_id <= 0:
        raise ValueError("policy_id must be positive.")
    value = conn.get(f"/replication/policies/{policy_id}")
    if not isinstance(value, dict):
        raise ValueError("Harbor replication policy response was not an object.")
    return value


def replication_execution(conn: HarborConnection, execution_id: int) -> dict:
    if execution_id <= 0:
        raise ValueError("execution_id must be positive.")
    value = conn.get(f"/replication/executions/{execution_id}")
    if not isinstance(value, dict):
        raise ValueError("Harbor replication execution response was not an object.")
    return value


def retention_tasks(
    conn: HarborConnection, policy_id: int, execution_id: int, limit: int = 50
) -> dict:
    if policy_id <= 0 or execution_id <= 0:
        raise ValueError("policy_id and execution_id must be positive.")
    return conn.list(f"/retentions/{policy_id}/executions/{execution_id}/tasks", limit=limit)


def quotas(conn: HarborConnection, limit: int = 50) -> dict:
    return conn.list("/quotas", limit=limit)


def project_audit_logs(conn: HarborConnection, project_name: str, limit: int = 50) -> dict:
    return conn.list(f"/projects/{segment(project_name)}/logs", limit=limit)


def health(conn: HarborConnection) -> dict:
    value = conn.get("/health")
    if not isinstance(value, dict):
        raise ValueError("Harbor /health did not return an object.")
    return value


def volumes(conn: HarborConnection) -> dict:
    value = conn.get("/systeminfo/volumes")
    if not isinstance(value, dict):
        raise ValueError("Harbor /systeminfo/volumes did not return an object.")
    return value


def gc_history(conn: HarborConnection, limit: int = 50) -> dict:
    return conn.list("/system/gc", limit=limit)


def replication_executions(
    conn: HarborConnection, limit: int = 50, status: str | None = None
) -> dict:
    params = {"status": status} if status else None
    return conn.list("/replication/executions", limit=limit, params=params)


def replication_tasks(conn: HarborConnection, execution_id: int, limit: int = 50) -> dict:
    if execution_id <= 0:
        raise ValueError("execution_id must be positive.")
    return conn.list(f"/replication/executions/{segment(execution_id)}/tasks", limit=limit)


def retention_policy(conn: HarborConnection, policy_id: int) -> dict:
    if policy_id <= 0:
        raise ValueError("policy_id must be positive.")
    value = conn.get(f"/retentions/{segment(policy_id)}")
    if not isinstance(value, dict):
        raise ValueError("Harbor retention policy response was not an object.")
    return value


def retention_executions(conn: HarborConnection, policy_id: int, limit: int = 50) -> dict:
    if policy_id <= 0:
        raise ValueError("policy_id must be positive.")
    return conn.list(f"/retentions/{segment(policy_id)}/executions", limit=limit)


def diagnosis(conn: HarborConnection, limit: int = 20) -> dict:
    """Correlate health, storage, GC, replication; preserve failed probes."""
    probes: dict[str, Any] = {}
    for name, call in (
        ("health", lambda: health(conn)),
        ("volumes", lambda: volumes(conn)),
        ("garbageCollection", lambda: gc_history(conn, limit)),
        ("replication", lambda: replication_executions(conn, limit)),
    ):
        try:
            probes[name] = {"data": call(), "error": None}
        except Exception as exc:  # noqa: BLE001 — report partial probe failure
            probes[name] = {"data": None, "error": f"{type(exc).__name__}: {exc}"}
    failed = [name for name, probe in probes.items() if probe["error"] is not None]
    return {
        "probes": probes,
        "failedProbes": failed,
        "complete": not failed,
        "note": "A failing probe means unknown status for that area, not an empty result.",
    }


def gc_execution(conn: HarborConnection, gc_id: int) -> dict:
    if gc_id <= 0:
        raise ValueError("gc_id must be positive.")
    value = conn.get(f"/system/gc/{gc_id}")
    if not isinstance(value, dict):
        raise ValueError("Harbor GC execution response was not an object.")
    return value


def gc_log(conn: HarborConnection, gc_id: int) -> dict:
    if gc_id <= 0:
        raise ValueError("gc_id must be positive.")
    return conn.get_text(f"/system/gc/{gc_id}/log")


def replication_task_log(conn: HarborConnection, execution_id: int, task_id: int) -> dict:
    if execution_id <= 0 or task_id <= 0:
        raise ValueError("execution_id and task_id must be positive.")
    return conn.get_text(f"/replication/executions/{execution_id}/tasks/{task_id}/log")


def retention_task_log(
    conn: HarborConnection, policy_id: int, execution_id: int, task_id: int
) -> dict:
    if min(policy_id, execution_id, task_id) <= 0:
        raise ValueError("policy_id, execution_id and task_id must be positive.")
    return conn.get_text(f"/retentions/{policy_id}/executions/{execution_id}/tasks/{task_id}")
