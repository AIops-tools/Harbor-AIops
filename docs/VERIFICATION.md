# Verification — Harbor AIops

## Source-backed API surface

The Harbor [v2.0 Swagger schema](https://github.com/goharbor/harbor/blob/main/api/v2.0/swagger.yaml), checked 2026-11-04, defines `GET /health`, `/systeminfo/volumes`, `/system/gc`, `/replication/executions`, `/replication/executions/{id}/tasks`, `/retentions/{id}`, and `/retentions/{id}/executions`. Collection responses use `page` and `page_size`; the implementation reads an extra row to measure truncation.

## Local verification

`tests/test_registry.py` uses a strict HTTP transport fake based on these paths. It covers authentication, multi-page GC history, exact-limit results, a 403 response, unknown paths, invalid IDs, and a partially failing diagnosis. Governance invariant tests come from the current tool line. The current local result is 133 passing tests, Ruff clean, Bandit Medium+ 0, and a successful source/wheel build on 2026-11-04.

## Not yet live verified

No Harbor instance was available: Docker is installed but its daemon was not running. No real API response, permissions matrix, asynchronous job completion, GC failure, retention dry-run, or write/undo cycle has been verified. Do not describe the source tree as production validated or published. The next gate is a disposable Harbor deployment with deliberately failed replication/retention and comparison to Harbor's own UI/API.
