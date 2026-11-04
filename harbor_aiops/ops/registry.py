"""Read-only Harbor registry operation and incident views."""

from __future__ import annotations

from typing import Any

from harbor_aiops.connection import HarborConnection, segment


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
