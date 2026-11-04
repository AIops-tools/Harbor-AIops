# Capabilities

Thirty-four Harbor reads cover health, volumes, statistics, projects, members, immutability rules, project summary, repositories, artifacts, tags, vulnerabilities, labels, robot metadata, quotas, project audit logs, scan metrics/logs, GC execution/history/log, replication policy/execution/task/log, retention policy/execution/task/log, and broad diagnosis. Two writes: `harbor_scan_artifact` and `harbor_create_tag`. Two governance tools: `undo_list`, `undo_apply`. Each list has a bounded envelope and measured truncation; plain-text logs are byte-capped. Robot-account `secret` fields are redacted.

Unsupported in this slice: starting or stopping GC, changing retention or replication policies, invoking retention dry-run jobs, deleting artifacts/tags, scanner administration, and project mutation. Request missing capabilities through an issue or PR with Harbor version and API response evidence.
