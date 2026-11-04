"""Governed Harbor incident and maintenance read tools."""

from typing import Optional

from harbor_aiops.governance import governed_tool
from harbor_aiops.mcp_server._shared import _get_connection, mcp, tool_errors
from harbor_aiops.ops import registry


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_statistics(target: Optional[str] = None) -> dict:
    """[READ] Get registry-wide project and repository counts."""
    return registry.statistics(_get_connection(target))


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_project_members(
    project: str, limit: int = 50, target: Optional[str] = None
) -> dict:
    """[READ] List a Harbor project's members with measured truncation."""
    return registry.project_members(_get_connection(target), project, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_immutable_rules(
    project: str, limit: int = 50, target: Optional[str] = None
) -> dict:
    """[READ] List tag immutability rules for a project."""
    return registry.immutable_rules(_get_connection(target), project, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_robot_accounts(limit: int = 50, target: Optional[str] = None) -> dict:
    """[READ] List robot account metadata with any returned secret redacted."""
    return registry.robot_accounts(_get_connection(target), limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_labels(limit: int = 50, target: Optional[str] = None) -> dict:
    """[READ] List Harbor labels with measured truncation."""
    return registry.labels(_get_connection(target), limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_scan_all_metrics(target: Optional[str] = None) -> dict:
    """[READ] Get metrics from the latest registry-wide scan."""
    return registry.scan_metrics(_get_connection(target))


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_scheduled_scan_metrics(target: Optional[str] = None) -> dict:
    """[READ] Get metrics from the latest scheduled registry-wide scan."""
    return registry.scan_metrics(_get_connection(target), scheduled=True)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_scan_log(
    project: str, repository: str, reference: str, report_id: str,
    target: Optional[str] = None,
) -> dict:
    """[READ] Read a bounded artifact scan report log by report ID."""
    return registry.scan_log(
        _get_connection(target), project, repository, reference, report_id
    )


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_gc_execution(gc_id: int, target: Optional[str] = None) -> dict:
    """[READ] Get one Harbor garbage-collection execution's current state."""
    return registry.gc_execution(_get_connection(target), gc_id)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_gc_log(gc_id: int, target: Optional[str] = None) -> dict:
    """[READ] Read the bounded plain-text log of a GC execution."""
    return registry.gc_log(_get_connection(target), gc_id)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_replication_task_log(
    execution_id: int, task_id: int, target: Optional[str] = None
) -> dict:
    """[READ] Read the bounded plain-text log of a replication task."""
    return registry.replication_task_log(_get_connection(target), execution_id, task_id)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_retention_task_log(
    policy_id: int, execution_id: int, task_id: int, target: Optional[str] = None
) -> dict:
    """[READ] Read the bounded plain-text log of a retention task."""
    return registry.retention_task_log(
        _get_connection(target), policy_id, execution_id, task_id
    )


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_projects(limit: int = 50, target: Optional[str] = None) -> dict:
    """[READ] List visible Harbor projects with measured truncation."""
    return registry.projects(_get_connection(target), limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_project(name: str, target: Optional[str] = None) -> dict:
    """[READ] Get one Harbor project by name or ID."""
    return registry.project(_get_connection(target), name)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_project_summary(name: str, target: Optional[str] = None) -> dict:
    """[READ] Get Harbor's repository, artifact and storage summary for a project."""
    return registry.project_summary(_get_connection(target), name)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_repositories(project: str, limit: int = 50, target: Optional[str] = None) -> dict:
    """[READ] List repositories inside a Harbor project."""
    return registry.repositories(_get_connection(target), project, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_artifacts(
    project: str, repository: str, limit: int = 50, target: Optional[str] = None
) -> dict:
    """[READ] List artifacts, tags and scan overviews in a repository."""
    return registry.artifacts(_get_connection(target), project, repository, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_artifact(
    project: str, repository: str, reference: str, target: Optional[str] = None
) -> dict:
    """[READ] Get one artifact with tags, scan overview and immutability status."""
    return registry.artifact(_get_connection(target), project, repository, reference)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_tags(
    project: str, repository: str, reference: str, limit: int = 50,
    target: Optional[str] = None,
) -> dict:
    """[READ] List tags and their immutable status for an artifact."""
    return registry.tags(_get_connection(target), project, repository, reference, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_vulnerabilities(
    project: str, repository: str, reference: str, target: Optional[str] = None
) -> dict:
    """[READ] Get Harbor's stored vulnerability report for an artifact."""
    return registry.vulnerabilities(_get_connection(target), project, repository, reference)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_replication_policies(limit: int = 50, target: Optional[str] = None) -> dict:
    """[READ] List replication policies with measured truncation."""
    return registry.replication_policies(_get_connection(target), limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_replication_policy(policy_id: int, target: Optional[str] = None) -> dict:
    """[READ] Get a replication policy by its Harbor ID."""
    return registry.replication_policy(_get_connection(target), policy_id)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_replication_execution(execution_id: int, target: Optional[str] = None) -> dict:
    """[READ] Get the current state of one replication execution."""
    return registry.replication_execution(_get_connection(target), execution_id)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_retention_tasks(
    policy_id: int, execution_id: int, limit: int = 50, target: Optional[str] = None
) -> dict:
    """[READ] List tasks of a retention execution, including per-task failures."""
    return registry.retention_tasks(_get_connection(target), policy_id, execution_id, limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_quotas(limit: int = 50, target: Optional[str] = None) -> dict:
    """[READ] List registry quota usage and limits."""
    return registry.quotas(_get_connection(target), limit)


@mcp.tool()
@governed_tool(risk_level="low")
@tool_errors()
def harbor_project_audit_logs(
    project: str, limit: int = 50, target: Optional[str] = None
) -> dict:
    """[READ] List a project's Harbor audit logs; not the MCP governance audit."""
    return registry.project_audit_logs(_get_connection(target), project, limit)


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
