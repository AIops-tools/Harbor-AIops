---
name: harbor-aiops
slug: harbor-aiops
displayName: "Harbor AIops"
summary: "Governed Harbor registry diagnosis for health, storage, GC, replication and retention."
license: MIT
homepage: https://github.com/AIops-tools/Harbor-AIops
tags: [aiops, mcp, governance, harbor, container-registry]
description: >
  Use this skill when a user asks to inspect a Harbor registry, diagnose a failing replication, check garbage collection or storage use, or inspect tag retention executions. The first release is read-only. For Docker hosts and Portainer use container-host-aiops; for Kubernetes cluster resources use k8s-aiops.
installer:
  kind: uv
  package: harbor-aiops
argument-hint: "[Harbor target, policy ID, or replication execution ID]"
allowed-tools:
  - Bash
metadata: {"openclaw":{"requires":{"anyBins":["uvx"]},"optional":{"env":["HARBOR_AIOPS_CONFIG","HARBOR_AIOPS_MASTER_PASSWORD"]},"homepage":"https://github.com/AIops-tools/Harbor-AIops","emoji":"📦","os":["macos","linux"]}}
---

# Harbor AIops

Use `harbor-aiops diagnose` for a broad first look, then `gc`, `replication`, `replication-tasks`, `retention`, or `retention-executions` for detail. Configure targets with `harbor-aiops init` and run `harbor-aiops doctor` to test access. The MCP server registers 8 Harbor read tools plus `undo_list` and `undo_apply`; no Harbor write produces an undo token in this version.

Do not claim a failed or unauthorized probe means there are zero failures. Check `error`, `complete`, and `truncated`. The diagnosis reports partial failures explicitly. Do not infer that a GC or retention execution succeeded from its existence; inspect its status and related details. See [guardrails](references/agent-guardrails.md) and [capabilities](references/capabilities.md).
