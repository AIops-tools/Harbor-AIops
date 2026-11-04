# Capabilities

Eight Harbor read tools: `harbor_health`, `harbor_volumes`, `harbor_gc_history`, `harbor_replication_executions`, `harbor_replication_tasks`, `harbor_retention_policy`, `harbor_retention_executions`, `harbor_diagnose`. Two governance tools: `undo_list`, `undo_apply`.

Unsupported in this slice: starting or stopping GC, changing retention or replication policies, invoking retention dry-run jobs, deleting artifacts, scanner administration, and project mutation. Request missing capabilities through an issue or PR with Harbor version and API response evidence.
