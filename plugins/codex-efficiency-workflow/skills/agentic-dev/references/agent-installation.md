# Agent Installation

Plugins currently package these custom-agent TOML files as templates. Install them into a Codex agent search location before asking for them by name.

From the plugin root, pass the repository that should receive the agents:

```bash
./scripts/install-agents.sh project /path/to/project
```

This installs to the target Git repository at `.codex/agents/`. If the path is omitted, the script uses the current working directory.

```bash
./scripts/install-agents.sh user
```

This installs to `~/.codex/agents/` for personal use across repositories.

Use `--force` only when intentionally replacing an existing template with the same filename.

## Suggested Agent Config

For cost-aware personal defaults, keep recursive spawning disabled and cap parallel threads below the Codex default:

```toml
[agents]
max_threads = 4
max_depth = 1
job_max_runtime_seconds = 1200
```

Use `~/.codex/config.toml` for personal defaults or `.codex/config.toml` for a project. Increase `max_threads` only for intentionally broad read-heavy fan-out; keep `max_depth = 1` unless recursive delegation is explicitly required.
