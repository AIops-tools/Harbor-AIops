---
name: harbor-aiops
slug: harbor-aiops
displayName: "Harbor AIops"
summary: "Governed Harbor registry diagnosis for health, storage, GC, replication and retention."
license: MIT
homepage: https://github.com/AIops-tools/Harbor-AIops
tags: [aiops, mcp, governance, harbor, container-registry]
description: >
  Use this skill when a user asks to inspect Harbor projects, repositories, artifacts, scans, vulnerabilities, quotas, GC, replication or retention, or to start an artifact scan or create a tag. For Docker hosts and Portainer use container-host-aiops; for Kubernetes cluster resources use k8s-aiops.
installer:
  kind: uv
  package: harbor-aiops
argument-hint: "[Harbor target, policy ID, or replication execution ID]"
allowed-tools:
  - Bash
metadata: {"openclaw":{"requires":{"anyBins":["uvx"]},"optional":{"env":["HARBOR_AIOPS_CONFIG","HARBOR_AIOPS_MASTER_PASSWORD"]},"homepage":"https://github.com/AIops-tools/Harbor-AIops","emoji":"📦","os":["macos","linux"]}}
---

# Harbor AIops

Use `harbor-aiops diagnose` for a broad first look, then `projects`, `repositories`, `artifacts`, `vulnerabilities`, `gc`, `replication`, or `retention` and their detail/log commands. Configure targets with `harbor-aiops init` and run `harbor-aiops doctor` to test access. The MCP server registers 26 Harbor read tools, two maintenance writes and two governance tools.

Do not claim a failed or unauthorized probe means there are zero failures. Check `error`, `complete`, and `truncated`. A scan returns `outcomeUnknown` until completion is observed; a tag write can return `outcomeUnknown` if post-read verification failed. Do not blindly retry either write. See [guardrails](references/agent-guardrails.md) and [capabilities](references/capabilities.md).
