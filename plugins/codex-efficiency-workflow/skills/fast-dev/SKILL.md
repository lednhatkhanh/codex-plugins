---
name: fast-dev
description: "Use for quick, cost-aware Codex work: focused edits, tests, review, validation, and deciding whether subagents are worth it."
metadata:
  short-description: Work fast with minimal context and cost
---

# Fast Dev

Use this skill when speed, efficiency, and cost control matter. Default to the simplest workflow that can still produce correct, verified work.

## Workflow

1. Classify the task before spending context.
   - `direct`: questions, one-file fixes, small refactors, focused tests, formatting, or obvious config edits.
   - `focused`: unfamiliar ownership, several files in one module, risky behavior, or validation triage.
   - `orchestrated`: independent work streams, broad codebase discovery, implementation plus docs/tests/review, or unclear critical path.

2. Choose the cheapest effective path.
   - For `direct`, keep work in the main agent. Read only the likely files and run the narrowest useful validation.
   - For `focused`, use at most one helper agent when it saves time or isolates a read-only/test/review task.
   - For `orchestrated`, use `$agentic-dev` and delegate only non-overlapping tasks.

3. Manage context deliberately.
   - Use `rg` and targeted file reads before broad scans.
   - Prefer repository instructions, package metadata, scripts, and adjacent code over assumptions.
   - Keep stable workflow rules in skills or agent files; keep dynamic repo facts late in prompts as file references or concise summaries.
   - Do not paste large docs or generated output into prompts when a file path, command, or short summary is enough.
   - Do not rewrite stable prompts, tool lists, or workflow text during a task unless that change is the task.

4. Validate in a ladder.
   - Start with the smallest command that exercises the changed behavior.
   - Broaden only after focused checks pass or when the change crosses package/service boundaries.
   - Separate likely regressions from environment, credentials, network, or pre-existing failures.

## Cost Rules

- Subagents are not free. Use them for context isolation, parallelism, or independent critique, not for routine work.
- Prefer small/fast model settings for read-only research, docs, validation triage, and narrow tests.
- Use high-reasoning agents for architecture, integration planning, difficult implementation, and final review only when the task risk warrants it.
- Avoid recursive delegation unless explicitly needed; broad fan-out increases cost, latency, and coordination risk.
- Do not run broad validation, dependency installs, or internet research unless the request or risk profile calls for it.
- Reuse the same compact prompt shape for repeated agent calls so stable prefixes stay cache-friendly.
- When delegating, specify the split, wait policy, and expected output shape in the prompt.

## Documentation And Internet

- For library, SDK, API, framework, CLI, or cloud-service details, follow the repository's documentation lookup rule first when one exists.
- Use current internet research when the user asks for it, when facts may have changed, or when external best practices are material to the decision.
- Prefer official and primary sources for tool behavior, configuration, and model guidance.

## Output

When finishing, report only:

- What changed.
- What validation ran and the result.
- Any meaningful residual risk or next focused command.

Keep the final answer short for small tasks.
