<!-- mcp-name: io.github.AIops-tools/harbor-aiops -->
# Harbor AIops

Governed, read-only diagnosis for Harbor container registries. The 0.1.0 source tree exposes 8 Harbor tools plus `undo_list` and `undo_apply` through MCP, and corresponding CLI commands. Every MCP tool is audited and budgeted by the bundled governance harness. No Harbor write operation or undo token is produced in this first slice.

## What it checks

- Component health and system volume use.
- Garbage collection execution history.
- Replication executions and their tasks.
- A retention policy and its execution history by actual policy ID.
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

The first slice is read-only. Retention execution, replication restart, GC start/stop and image deletion are withheld until their actual asynchronous outcomes and failure states can be verified against a disposable Harbor deployment. See [verification](docs/VERIFICATION.md). Missing operations and live-environment feedback are welcome as issues or PRs.

## Development

`uv run pytest -q`, `uv run ruff check .`, and `uv run bandit -r harbor_aiops -ll` are local checks. Root handbook gates must pass before release.
