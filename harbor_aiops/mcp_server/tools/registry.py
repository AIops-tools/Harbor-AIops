"""Governed Harbor incident and maintenance read tools."""

from typing import Optional

from harbor_aiops.governance import governed_tool
from harbor_aiops.mcp_server._shared import _get_connection, mcp, tool_errors
from harbor_aiops.ops import registry


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_health(target: Optional[str] = None) -> dict:
    """[READ] Get Harbor component health; unknown components remain visible."""
    return registry.health(_get_connection(target))


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_volumes(target: Optional[str] = None) -> dict:
    """[READ] Get Harbor storage volume usage from the system-info endpoint."""
    return registry.volumes(_get_connection(target))


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_gc_history(limit: int = 50, target: Optional[str] = None) -> dict:
    """[READ] List garbage-collection executions with measured truncation."""
    return registry.gc_history(_get_connection(target), limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_replication_executions(
    limit: int = 50, status: Optional[str] = None, target: Optional[str] = None
) -> dict:
    """[READ] List replication executions, optionally filtered by upstream status."""
    return registry.replication_executions(_get_connection(target), limit, status)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_replication_tasks(
    execution_id: int, limit: int = 50, target: Optional[str] = None
) -> dict:
    """[READ] List tasks for one replication execution."""
    return registry.replication_tasks(_get_connection(target), execution_id, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_retention_policy(policy_id: int, target: Optional[str] = None) -> dict:
    """[READ] Get one retention policy by its actual Harbor policy id."""
    return registry.retention_policy(_get_connection(target), policy_id)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_retention_executions(
    policy_id: int, limit: int = 50, target: Optional[str] = None
) -> dict:
    """[READ] List executions of one retention policy with measured truncation."""
    return registry.retention_executions(_get_connection(target), policy_id, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_diagnose(limit: int = 20, target: Optional[str] = None) -> dict:
    """[READ] Correlate health, volume, GC and replication probes; show partial failures."""
    return registry.diagnosis(_get_connection(target), limit)
