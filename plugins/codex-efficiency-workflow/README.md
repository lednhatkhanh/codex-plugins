# Codex Efficiency Workflow

Reusable Codex skills and optional custom-agent templates for fast, cost-aware software work across repositories.

## What is included

- `fast-dev`: default skill for small and medium work where speed, efficiency, and low token spend matter.
- `agentic-dev`: explicit multi-agent workflow for complex work that benefits from bounded parallel research, implementation, testing, docs, verification, or review.
- `assets/agents/*.toml`: generalized custom-agent templates adapted from a project-local workflow.
- `references/codex-agent-config.toml`: suggested cost-aware subagent settings.
- `scripts/install-agents.sh`: copies the bundled agent templates into either the current repository or the user Codex home.
- `scripts/validate-plugin.sh`: validates the plugin manifest and agent TOML syntax.

## Install bundled agents

From the plugin root, pass the repository that should receive the agents:

```bash
./scripts/install-agents.sh project /path/to/project
```

This installs to the target Git repository at `.codex/agents/`. If the path is omitted, the script uses the current working directory.

For personal agents available across repositories:

```bash
./scripts/install-agents.sh user
```

The scripts refuse to overwrite existing agent files unless `--force` is passed.

## Usage

Use `$fast-dev` for normal work. It keeps tasks local by default, reads only the context needed, and escalates validation in a narrow-to-broad ladder.

Use `$agentic-dev` when the task is large enough to justify subagents. It provides dispatch rules and prompt templates for the bundled agent roles.

The multi-agent skill disables implicit invocation in `agents/openai.yaml` so Codex does not load or apply orchestration guidance accidentally.

The bundled agent model defaults follow Codex subagent guidance: `gpt-5.5` for demanding orchestration, implementation, and review; `gpt-5.4-mini` for read-heavy research, docs, focused tests, and validation triage.

## Suggested Codex config

Codex defaults `agents.max_threads` to `6` and `agents.max_depth` to `1`. For personal cost control, this plugin recommends lower concurrency and keeping recursive fan-out disabled:

```toml
[agents]
max_threads = 4
max_depth = 1
job_max_runtime_seconds = 1200
```

See `references/codex-agent-config.toml` for a copyable snippet. Apply it manually to `~/.codex/config.toml` or a project `.codex/config.toml`; this plugin does not edit global config.
