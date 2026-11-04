# Harbor AIops agent guardrails

| Enforced in code | Location |
|---|---|
| Every MCP tool is audited, budgeted and carries a risk annotation. | `governance/decorators.py`, `mcp_server/_annotations.py` |
| Agent-supplied IDs and the double-encoded repository path stay within Harbor's API; writes are limited to scan and tag creation. | `connection.py:segment`, `connection.py:repository_segment`, `connection.py:write` |
| List truncation is measured by fetching one extra item across real page boundaries. | `connection.py:list` |
| A failed health/volume/GC/replication probe remains an error, not an empty list. | `ops/registry.py:diagnosis` |
| Passwords are read from the encrypted secret store, with an optional legacy environment fallback. | `config.py:_resolve_secret`, `secretstore.py` |
| Scan acceptance is unknown until checked; tag creation requires a nontruncated absence check and a confirming post-read. | `ops/writes.py:scan_artifact`, `ops/writes.py:create_tag` |

The caller should inspect asynchronous job statuses and not call an execution successful merely because an ID exists. After `outcomeUnknown`, read current state before retrying. These writes have no safe general undo: a scan cannot be reversed, and a newly created tag can become immutable or move while the undo waits.
