# CLI reference

- `harbor-aiops init`: configure one target and encrypted password.
- `harbor-aiops secret set <name>`: replace a target password.
- `harbor-aiops doctor`: test Harbor health access.
- `harbor-aiops diagnose`: correlated read-only probes.
- `harbor-aiops health`, `volumes`, `gc`, `replication`, `replication-tasks <execution-id>`, `retention <policy-id>`, `retention-executions <policy-id>`: focused reads.
- `harbor-aiops mcp`: start the stdio MCP server.
- `harbor-aiops undo list` and `undo apply`: common governance interface; no Harbor write records a token in this slice.

Use `--target` for a named target and `--limit` on lists. CLI commands call the governed MCP tool functions, so their Harbor reads are audited.
