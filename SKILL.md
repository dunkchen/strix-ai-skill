---
name: strix-pentest-knowledge
description: Index into Strix's internal pentest knowledge packs (methodology, vulnerability classes, tool playbooks, frameworks, protocols, cloud, recon, coordination). Use when planning or executing any security test / penetration test / vulnerability assessment / AppSec review through the strix_sandbox MCP tools, when choosing technique for a specific vuln type, framework, protocol or target platform, when orchestrating recon-to-exploitation across sub-agents, or when scoring and writing up findings. Packs are plain markdown on disk, load only the few relevant to the current task, never copy them out in full.
---

# Strix pentest knowledge packs

Root: `D:/code/work/strix-main/strix/skills/` — read packs directly with the Read tool from the host path (they are plain `.md` files, no sandbox needed). Category overview: read `D:/code/work/strix-main/strix/skills/README.md` if unsure which pack fits.

Select at most ~5 packs per agent/task (Strix's own per-agent budget).

## Always-load first (Strix's built-in policy, mirrors agents/prompt.py `_resolve_skills`)

- Scan depth: `scan_modes/deep.md` (full chain: recon→validate→exploit→report) | `standard.md` | `quick.md` (fast, high-confidence only) | `diff.md` (change-scoped overlay) — pick the mode matching the user's ask.
- `tooling/agent_browser.md` — browser automation workflow (snapshot/@ref loop, per-agent `--session`, gotchas).
- `tooling/python.md` — writing/running Python in the sandbox incl. Caido proxy automation module.
- `analysis/counterevidence.md` — closure discipline: actively try to disprove a finding before reporting.
- `analysis/severity_calibration.md` — severity/impact rubric for scoring findings.
- Acting as commander/orchestrator: `coordination/root_agent.md` — delegation, parallel specialist agents, communication patterns.
- White-box / code-review targets add: `coordination/source_aware_whitebox.md`, `custom/source_aware_sast.md`, `analysis/source_aware_discovery.md`, `analysis/fix_verification.md`.

## On-demand catalog (decide by current target/task)

**vulnerabilities/** — per-class testing + validation + exploitation playbooks:
- Injection: `sql_injection.md` `nosql_injection.md` `ssti.md` `xss.md` `xxe.md` `header_injection.md` `argument_injection.md`
- Server-side: `ssrf.md` `rce.md` `insecure_file_uploads.md` `insecure_deserialization.md` `path_traversal_lfi_rfi.md` `prototype_pollution.md` `mass_assignment.md` `open_redirect.md` `csrf.md`
- Auth/access: `authentication_jwt.md` `idor.md` `broken_function_level_authorization.md` `weak_password_detection.md`
- State/protocol: `race_conditions.md` `business_logic.md` `http_request_smuggling.md` `semantic_confusion.md`
- Info/reporting: `information_disclosure.md` `subdomain_takeover.md`
- AI/modern surface: `llm_prompt_injection.md` `agentic_system_security.md` (MCP/tool-ecosystem authority tests) `browser_security.md` (postMessage, XS-Leaks, service workers)

**tooling/** — CLI playbooks for the sandbox (all run via `sandbox_exec`):
`nmap.md` (ports/raw) `naabu.md` (fast port scan) `subfinder.md` (subdomain enumeration) `httpx.md` (HTTP probing) `katana.md` (crawling) `ffuf.md` (fuzzing/dir listing) `nuclei.md` (template vuln scanner) `sqlmap.md` (injection automation) `semgrep.md` (static analysis) `hurl.md` (declarative HTTP request scripts)

**frameworks/** — target-stack specifics: `django.md` `fastapi.md` `nestjs.md` `nextjs.md`

**protocols/** — `graphql.md` (introspection, batching, depth abuse) `oauth.md` (flow redirection, state confusion)

**technologies/** — third-party services: `supabase.md` `firebase.md` `auth0.md` `grafana_prometheus.md` `active_directory.md` `electron_desktop_apps.md` `llm_applications.md`

**cloud/** — `aws.md` `azure.md` `gcp.md` `kubernetes.md`

**reconnaissance/** — `asset_discovery.md` (attack-surface mapping) `infrastructure_lifecycle.md` (abandoned/mutable dependencies, takeover candidates)

**custom/** — `api_spec_testing.md` (OpenAPI-driven) `dependency_cve_scanning.md` (SCA/known-CVE workflow) `npx_confusion.md` (package-runner identity abuse) `source_aware_sast.md`

## Rules for use

1. Read the relevant packs **at task start**, before building the threat model / picking tools.
2. Sub-agents don't inherit your reads: when delegating, put the concrete pack paths into the sub-agent prompt ("first Read D:/.../sql_injection.md").
3. Before reporting any finding as a vulnerability, apply `analysis/counterevidence.md`; score with `analysis/severity_calibration.md`.
4. Packs guide thinking only — they add no tool capability; execution stays with the strix_sandbox MCP tools.
