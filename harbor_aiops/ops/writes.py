"""Narrow Harbor maintenance writes with before-state and post-read checks."""

from __future__ import annotations

import re

from harbor_aiops.connection import HarborConnection, repository_segment, segment
from harbor_aiops.governance import mark_unknown
from harbor_aiops.ops import registry


def _artifact_path(project: str, repository: str, reference: str) -> str:
    return (
        f"/projects/{segment(project)}/repositories/{repository_segment(repository)}"
        f"/artifacts/{segment(reference)}"
    )


def scan_artifact(
    conn: HarborConnection, project: str, repository: str, reference: str,
    dry_run: bool = False,
) -> dict:
    before = registry.artifact(conn, project, repository, reference)
    if dry_run:
        return {"dryRun": True, "artifact": before, "wouldStartScan": True}
    response = conn.write(
        "POST", _artifact_path(project, repository, reference) + "/scan",
        expected_status=202,
    )
    return mark_unknown({
        "accepted": True, "response": response, "artifactDigest": before.get("digest"),
        "hint": "Inspect the artifact scan overview before treating the scan as complete.",
    })


def create_tag(
    conn: HarborConnection, project: str, repository: str, reference: str,
    tag: str, dry_run: bool = False,
) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", tag):
        raise ValueError("Invalid OCI tag name.")
    before = registry.artifact(conn, project, repository, reference)
    digest = before.get("digest")
    if not isinstance(digest, str) or not digest:
        raise ValueError("Harbor did not return an artifact digest; refusing tag creation.")
    existing = registry.tags(conn, project, repository, digest, limit=500)
    if existing["truncated"]:
        raise ValueError("Tag list is truncated; cannot prove the proposed tag is absent.")
    if any(isinstance(item, dict) and item.get("name") == tag for item in existing["items"]):
        raise ValueError("Tag already exists on this artifact.")
    if dry_run:
        return {"dryRun": True, "artifactDigest": digest, "wouldCreateTag": tag}
    response = conn.write(
        "POST", _artifact_path(project, repository, digest) + "/tags",
        body={"name": tag}, expected_status=201,
    )
    try:
        after = registry.tags(conn, project, repository, digest, limit=500)
        visible = any(
            isinstance(item, dict) and item.get("name") == tag for item in after["items"]
        )
    except Exception as exc:
        return mark_unknown({"accepted": True, "response": response,
                             "verificationError": f"{type(exc).__name__}: {exc}"})
    if after["truncated"] or not visible:
        return mark_unknown({"accepted": True, "response": response,
                             "verificationError": "Tag not yet visible or list truncated."})
    return {"created": True, "tag": tag, "artifactDigest": digest, "response": response}
