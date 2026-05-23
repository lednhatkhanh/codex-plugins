# AGENTS.md

## Purpose

Maintain this repository as a personal Codex plugin marketplace.

## Repository Scope

This repository is no longer a standalone skills workspace.

- Plugins live under `plugins/<plugin-name>/`.
- The marketplace catalog lives at `.agents/plugins/marketplace.json`.
- Skills must be bundled inside plugins at `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`.
- Do not add top-level skill directories such as `use-modern-go/` or `use-nuqs/`.
- Do not add canonical prompt files for standalone skills. Put plugin-specific references inside the plugin.

## Plugin Workflow

1. Identify the target plugin under `plugins/`.
2. Update `.codex-plugin/plugin.json` only with fields supported by Codex plugin manifests.
3. Keep marketplace entries aligned with plugin folders:
   - `plugins/<plugin-name>/`
   - `plugin.json` field `"name": "<plugin-name>"`
   - `.agents/plugins/marketplace.json` entry `"name": "<plugin-name>"`
   - marketplace `source.path: "./plugins/<plugin-name>"`
4. Put reusable workflows in bundled skills, not in repo-level instructions.
5. Put optional install helpers, templates, or generated assets inside the plugin that owns them.

## Marketplace Rules

- Treat `.agents/plugins/marketplace.json` as the source of truth for what Codex can install from this repo.
- Append new plugins unless the user explicitly asks to reorder.
- Preserve `interface.displayName` unless the user asks to rename the marketplace.
- Every plugin entry must include:
  - `policy.installation`
  - `policy.authentication`
  - `category`
- Default new entries to:
  - `policy.installation: "AVAILABLE"`
  - `policy.authentication: "ON_INSTALL"`
  - `category: "Productivity"`
- Do not add `policy.products` unless explicitly requested.

## Plugin Manifest Rules

- Every plugin must include `.codex-plugin/plugin.json`.
- Keep plugin names lowercase hyphen-case.
- `plugin.json` must include real values for `name`, `version`, `description`, `author.name`, and `interface`.
- Use strict semver for `version`.
- Include `"skills": "./skills/"` only when a `skills/` directory exists.
- Include `apps`, `mcpServers`, images, screenshots, or URLs only when the files/URLs are real and intended for install-surface metadata.
- Put lifecycle hooks in `hooks/hooks.json` by default. Add a manifest `hooks` field only when intentionally overriding the default hook path.
- Do not add unsupported manifest fields that validation rejects.
- Do not leave `[TODO: ...]` placeholders.

## Validation

Run before finishing any plugin or marketplace change:

```bash
python3 scripts/validate-marketplace.py
```

For plugin-local validation, use the plugin script when present:

```bash
plugins/<plugin-name>/scripts/validate-plugin.sh
```

## Editing Rules

- Prefer small, focused changes.
- Do not create global Codex artifacts unless explicitly requested.
- Do not modify `~/.codex/config.toml`, `~/.codex/agents`, or personal marketplace files unless explicitly requested.
- Do not remove user-created plugins or marketplace entries unless explicitly requested.
