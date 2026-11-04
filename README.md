<!-- mcp-name: io.github.AIops-tools/harbor-aiops -->
# Harbor AIops

Governed Harbor container-registry operations with 38 MCP tools and corresponding CLI commands. Every call is audited and budgeted by the bundled governance harness. Two maintenance operations—artifact scan and tag creation—have dry-run previews; uncertain results are reported as `outcomeUnknown`.

## What it checks

- Component health and system volume use.
- Projects, repository inventory, artifacts, tags, vulnerability reports, quotas and project audit logs.
- Registry statistics, project members, tag immutability rules, labels and robot metadata (secrets redacted).
- Latest registry-wide and scheduled scan metrics, plus bounded artifact scan report logs.
- Garbage collection execution history.
- GC execution details and bounded plain-text logs.
- Replication policies, executions, tasks and bounded task logs.
- Retention policy, execution, tasks and bounded task logs by actual IDs.
- `harbor_diagnose` combines health, volume, GC and replication observations. Failed probes appear as errors with `data: null`.

Lists have `items`, `returned`, `limit`, and measured `truncated` fields. They are capped at 500 records per call.

## Setup from source

Requires Python 3.11+, `uv`, and a Harbor instance. Install locally with `uv sync --dev`. Run `uv run harbor-aiops init` to configure an HTTPS target and encrypt its password, or create `~/.harbor-aiops/config.yaml` with a `targets` list:

```yaml
targets:
  - name: primary
    host: harbor.example.com
    username: robot$ops
    scheme: https
    port: 443
    verify_ssl: true
    timeout: 30
```

Run `uv run harbor-aiops secret set primary`, then `uv run harbor-aiops doctor` and `uv run harbor-aiops diagnose`. The MCP entry point is `uv run harbor-aiops-mcp`. Set `HARBOR_AIOPS_MASTER_PASSWORD` for noninteractive secret-store access. TLS verification is enabled by default; `ca_file` accepts a custom CA PEM.

## Scope and verification

The `scan-artifact` command starts an asynchronous scan and reports an unknown final outcome until its status is checked. `create-tag` proves the tag was absent and checks that it appeared after the write; it does not mint an undo token because immutability and later artifact changes can make inverse deletion unsafe. Retention execution, replication restart, GC start/stop, artifact deletion and policy changes remain outside this release until their actual outcomes and recovery paths can be verified on disposable Harbor. See [verification](docs/VERIFICATION.md). Missing operations and live-environment feedback are welcome as issues or PRs.

## Development

`uv run pytest -q`, `uv run ruff check .`, and `uv run bandit -r harbor_aiops -ll` are local checks. Root handbook gates must pass before release.
