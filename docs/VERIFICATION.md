# Verification — Harbor AIops

## Source-backed API surface

The Harbor [v2.0 Swagger schema](https://github.com/goharbor/harbor/blob/main/api/v2.0/swagger.yaml), checked 2026-11-04, defines the project/repository/artifact/tag, quota, GC, replication, retention and project-log paths used here, plus `/statistics`, project members, immutable-tag rules, robot accounts, labels, both scan-metrics endpoints and artifact scan logs. It explicitly requires a slash in a `repository_name` path argument to be encoded twice. GC, replication-task and retention-task logs produce `text/plain`. Artifact scan is `POST .../scan` with HTTP 202; tag creation is `POST .../tags` with HTTP 201. Collection responses use `page` and `page_size`; the implementation reads an extra row to measure truncation.

## Local verification

`tests/test_registry.py` uses a strict HTTP transport fake based on these paths and a loopback HTTP server for proxy isolation. It covers authentication, multi-page GC history, exact-limit results, 403 responses, repository double encoding, bounded plain-text logs, dry-run tag creation, post-read tag verification, robot-secret redaction, new read endpoint shapes, async scan uncertainty, lost write response, HTTP 500 ambiguity, redirect rejection and a partially failing diagnosis. Governance invariant tests come from the current tool line. Current result: 142 passing tests, Ruff clean, Bandit 0 Medium+ and wheel/sdist build on 2026-11-04.

The current 0.2.0 candidate wheel was rebuilt and installed into a new environment outside the source tree; its MCP registry reports 38 tools. An earlier 0.2.0 candidate wheel was also installed outside the source tree; `harbor_aiops.__file__` resolved under `site-packages`. Its CLI ran four cases against a strict loopback HTTP stub: health, project listing, tag preview and real tag creation. The stub saw exactly one POST; the real create returned success only after a confirming GET. This validates packaging and request shape, not a real Harbor server.

## Not yet live verified

No Harbor instance was available: Docker is installed but its daemon was not running. No real Harbor API response, permissions matrix, asynchronous job completion, GC failure, retention dry-run, or write cycle has been verified. These writes record no undo token. Do not describe the package as production validated. The next gate is a disposable Harbor deployment with deliberately failed replication/retention and comparison to Harbor's own UI/API.
