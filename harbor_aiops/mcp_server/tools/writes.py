"""Governed Harbor scan and tag maintenance tools."""

from typing import Optional

from harbor_aiops.governance import governed_tool
from harbor_aiops.mcp_server._shared import _get_connection, mcp, tool_errors
from harbor_aiops.ops import writes


@mcp.tool()
@governed_tool(risk_level="medium")
@tool_errors()
def harbor_scan_artifact(
    project: str, repository: str, reference: str, dry_run: bool = False,
    target: Optional[str] = None,
) -> dict:
    """[WRITE] Start an artifact scan; accepted does not mean scan completed."""
    return writes.scan_artifact(
        _get_connection(target), project, repository, reference, dry_run
    )


@mcp.tool()
@governed_tool(risk_level="medium")
@tool_errors()
def harbor_create_tag(
    project: str, repository: str, reference: str, tag: str,
    dry_run: bool = False, target: Optional[str] = None,
) -> dict:
    """[WRITE] Create a tag only if its absence was proven and verify it appeared."""
    return writes.create_tag(
        _get_connection(target), project, repository, reference, tag, dry_run
    )


@mcp.tool()
@governed_tool(risk_level="high")
@tool_errors()
def harbor_delete_tag(
    project: str, repository: str, reference: str, tag: str,
    dry_run: bool = False, target: Optional[str] = None,
) -> dict:
    """[WRITE] Delete one verified, mutable tag; no safe undo is minted."""
    return writes.delete_tag(
        _get_connection(target), project, repository, reference, tag, dry_run
    )
