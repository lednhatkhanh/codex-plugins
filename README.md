# Personal Codex Plugin Marketplace

This repository is a personal Codex plugin marketplace. It is meant to be cloned, committed, and added to Codex as a repo-scoped marketplace source.

## Layout

```text
.agents/
└── plugins/
    └── marketplace.json      # Codex marketplace catalog
plugins/
└── <plugin-name>/
    ├── .codex-plugin/
    │   └── plugin.json       # Required plugin manifest
    ├── skills/               # Bundled skills
    ├── assets/               # Optional templates/assets
    └── scripts/              # Optional plugin-local helpers
scripts/
└── validate-marketplace.py   # Repo validation
```

Do not add standalone top-level skills to this repo. Every reusable skill should be packaged inside a plugin under `plugins/<plugin-name>/skills/`.

## Current Plugins

| Plugin | Purpose |
| --- | --- |
| `codex-efficiency-workflow` | Cost-aware Codex workflows and optional reusable custom-agent templates. |

## Add This Marketplace To Codex

From this repository root:

```bash
codex plugin marketplace add .
```

Then restart Codex and open `/plugins`. The marketplace name is `personal-codex-marketplace`.

## Add A Plugin

Use `plugin-creator` for scaffolding when possible, but target this repository:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/create_basic_plugin.py" <plugin-name> \
  --path ./plugins \
  --marketplace-path ./.agents/plugins/marketplace.json \
  --with-skills \
  --with-marketplace
```

Then edit `plugins/<plugin-name>/.codex-plugin/plugin.json` and add bundled skills under `plugins/<plugin-name>/skills/`.

Marketplace rules:

- Keep plugin folder names, marketplace entry names, and `plugin.json` names identical.
- Keep marketplace `source.path` as `./plugins/<plugin-name>`.
- Always include `policy.installation`, `policy.authentication`, and `category`.
- Use `AVAILABLE` and `ON_INSTALL` by default.
- Omit apps, MCP servers, icons, logos, and screenshots unless the referenced files exist.
- Put lifecycle hooks at `hooks/hooks.json` unless a plugin intentionally needs a custom manifest `hooks` entry.

## Validate

Run before committing:

```bash
python3 scripts/validate-marketplace.py
```

This checks marketplace shape, plugin manifests, bundled skill frontmatter, and bundled agent TOML templates without third-party Python dependencies.
