# Source Basis

This skill was generalized from a project-local Codex workflow and updated against public guidance available on 2026-05-23.

Sources consulted:

- OpenAI Codex Skills docs: skills are reusable workflows, loaded with progressive disclosure, and frontmatter descriptions compete for initial context budget.
- OpenAI Codex Plugins docs: plugins bundle reusable skills, app integrations, and MCP servers for installation and distribution.
- OpenAI Codex Build Plugins docs: plugin manifests live at `.codex-plugin/plugin.json`; paths are relative to the plugin root; repo marketplaces live at `.agents/plugins/marketplace.json`; `source.path` is relative to the marketplace root; hooks can use the default `hooks/hooks.json` path or a manifest `hooks` override.
- OpenAI Codex Subagents concepts docs: subagents are explicit, cost more than single-agent runs, work best for read-heavy parallel tasks, and should receive prompts that define work split, wait policy, and output shape.
- OpenAI Codex Subagents configuration docs: custom agent files live in `~/.codex/agents/` or `.codex/agents/`, require name/description/developer instructions, can include supported `config.toml` keys, and inherit parent sandbox/approval behavior unless overridden.
- OpenAI Codex Subagents global settings docs: `agents.max_threads` defaults to 6, `agents.max_depth` defaults to 1, and keeping depth at 1 avoids recursive fan-out cost and predictability risk.
- OpenAI Codex Models docs: start demanding agents with `gpt-5.5`, use `gpt-5.4-mini` for faster/lower-cost supporting workers, and reserve high reasoning effort for complex logic or edge-case review.
- OpenAI Codex AGENTS.md docs: repo and global instructions are layered from broader to more specific scopes.
- Anthropic Building Effective Agents guidance: match agent/workflow complexity to task value; use parallel and orchestrator-worker patterns when the subtasks justify them.
- OpenAI prompt-caching guidance: stable repeated prefixes can reduce latency and cost; keep dynamic content late and compact, and monitor cache hit rate when using the API directly.
