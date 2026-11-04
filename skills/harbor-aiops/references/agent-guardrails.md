# Harbor AIops agent guardrails

| Enforced in code | Location |
|---|---|
| Every MCP tool is audited, budgeted and carries a risk annotation. | `governance/decorators.py`, `mcp_server/_annotations.py` |
| Harbor operations in this slice use GET only. | `connection.py:get`, `mcp_server/tools/registry.py` |
| List truncation is measured by fetching one extra item across real page boundaries. | `connection.py:list` |
| A failed health/volume/GC/replication probe remains an error, not an empty list. | `ops/registry.py:diagnosis` |
| Passwords are read from the encrypted secret store, with an optional legacy environment fallback. | `config.py:_resolve_secret`, `secretstore.py` |

The caller should inspect asynchronous job statuses and not call an execution successful merely because an ID exists. In this version there are no Harbor writes to retry or undo. `undo_apply` is present only as part of the common governance interface.
