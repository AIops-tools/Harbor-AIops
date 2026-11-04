# CLI reference

- `harbor-aiops init`: configure one target and encrypted password.
- `harbor-aiops secret set <name>`: replace a target password.
- `harbor-aiops doctor`: test Harbor health access.
- `harbor-aiops diagnose`: correlated health, volume, GC and replication probes.
- Inventory: `projects`, `project <name>`, `project-summary <name>`, `repositories <project>`, `artifacts <project> <repo>`, `artifact <project> <repo> <reference>`, `tags`, `vulnerabilities`, `quotas`, `project-audit-logs`.
- Maintenance reads: `health`, `volumes`, `gc`, `gc-execution`, `gc-log`, `replication`, `replication-policies`, `replication-policy`, `replication-execution`, `replication-tasks`, `replication-task-log`, `retention`, `retention-executions`, `retention-tasks`, `retention-task-log`.
- Writes: `scan-artifact <project> <repo> <reference>` and `create-tag <project> <repo> <reference> <tag>`, both with `--dry-run`. Real CLI calls require two confirmations; unknown outcomes exit 2.
- `harbor-aiops mcp`: start the stdio MCP server.
- `harbor-aiops undo list` and `undo apply`: common governance interface; these Harbor writes record no undo token.

Use `--target` for a named target and `--limit` on lists. CLI commands call the governed MCP tool functions, so their Harbor reads are audited.
