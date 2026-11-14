"""Governed Harbor scan and tag maintenance tools."""

from typing import Annotated, Optional

from pydantic import Field

from harbor_aiops.governance import governed_tool
from harbor_aiops.mcp_server._shared import _get_connection, mcp, tool_errors
from harbor_aiops.ops import writes


@mcp.tool()
@governed_tool(risk_level="medium")
@tool_errors()
def harbor_scan_artifact(
    project: Annotated[str, Field(description="Harbor project name containing the resource.")],
    repository: Annotated[str, Field(description="Repository name within the Harbor project.")],
    reference: Annotated[
        str,
        Field(description=("Artifact digest or tag identifying one artifact in the repository.")),
    ],
    dry_run: Annotated[
        bool,
        Field(description=("Preview the guarded operation without making the upstream change.")),
    ] = False,
    target: Annotated[
        Optional[str],
        Field(description=("Configured target name; omit to use the default connection.")),
    ] = None,
) -> dict:
    """[WRITE] Start an artifact scan; accepted does not mean scan completed.

    Use to request a scan of one artifact; a request acceptance does not establish scan
    completion.

    Result: a guarded outcome; dry_run makes no upstream change, and scan acceptance does not
    prove completion.
    """
    return writes.scan_artifact(_get_connection(target), project, repository, reference, dry_run)


@mcp.tool()
@governed_tool(risk_level="medium")
@tool_errors()
def harbor_create_tag(
    project: str,
    repository: str,
    reference: str,
    tag: str,
    dry_run: bool = False,
    target: Optional[str] = None,
) -> dict:
    """[WRITE] Create a tag only if its absence was proven and verify it appeared."""
    return writes.create_tag(_get_connection(target), project, repository, reference, tag, dry_run)


@mcp.tool()
@governed_tool(risk_level="high")
@tool_errors()
def harbor_delete_tag(
    project: Annotated[str, Field(description="Harbor project name containing the resource.")],
    repository: Annotated[str, Field(description="Repository name within the Harbor project.")],
    reference: Annotated[
        str,
        Field(description=("Artifact digest or tag identifying one artifact in the repository.")),
    ],
    tag: Annotated[
        str, Field(description="Tag name to create or delete on the selected artifact.")
    ],
    dry_run: Annotated[
        bool,
        Field(description=("Preview the guarded operation without making the upstream change.")),
    ] = False,
    target: Annotated[
        Optional[str],
        Field(description=("Configured target name; omit to use the default connection.")),
    ] = None,
) -> dict:
    """[WRITE] Delete one verified, mutable tag; no safe undo is minted.

    Use only for a verified mutable tag. The operation is destructive and creates no safe undo
    token.

    Result: a guarded outcome; dry_run makes no upstream change, and a real tag change is
    checked by a follow-up read.
    """
    return writes.delete_tag(_get_connection(target), project, repository, reference, tag, dry_run)
