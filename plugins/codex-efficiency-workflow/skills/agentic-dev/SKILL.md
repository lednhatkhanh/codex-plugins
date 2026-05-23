---
name: agentic-dev
description: "Use for explicit multi-agent Codex work: subagents, orchestration, parallel research, tests, docs, verification, and review."
metadata:
  short-description: Run bounded multi-agent delivery
---

# Agentic Dev

Use this skill only when multi-agent work is explicitly requested or when the task is large enough that parallelism, context isolation, or independent review clearly justifies the extra cost.

Every subagent prompt must define the work split, whether to wait for the result before continuing, and the exact output shape expected from the subagent.

## Agent Catalog

The bundled templates live in `assets/agents/`. Install them with `scripts/install-agents.sh` before relying on the custom names.

- `delivery-orchestrator`: Plans complex work, splits non-overlapping tasks, and integrates results.
- `codebase-researcher`: Read-only discovery for architecture, ownership, dependencies, current behavior, and edit surfaces.
- `implementation-builder`: Focused code-change worker with explicit file/module ownership.
- `test-author`: Focused test author for changed behavior.
- `verification-engineer`: Runs or triages the narrowest meaningful validation.
- `docs-maintainer`: Updates docs made stale by code/config changes.
- `quality-reviewer`: Independent bug-finding review for correctness, security, regressions, maintainability, and missing validation.

## Dispatch Rules

1. Keep the main agent responsible for blockers, integration, user-facing decisions, and merge-sensitive edits.
2. Delegate research before editing when ownership or behavior is unclear.
3. Delegate implementation only with explicit ownership: files, packages, modules, or a disjoint feature slice.
4. Delegate tests when behavior is clear and test files are non-overlapping with implementation edits.
5. Delegate verification when commands can run independently or the validation scope is already known.
6. Delegate docs only when user-facing setup, behavior, API, or operations changed.
7. Delegate review once the patch is coherent enough for independent critique.
8. Do not spawn overlapping write scopes. Do not use recursive delegation unless explicitly requested.
9. Prefer read-heavy parallelism first: exploration, tests, triage, summarization, and review.
10. Prefer one researcher plus one reviewer before adding write-capable workers.

## Prompt Templates

### Research

```text
Use codebase-researcher to find where <behavior> is implemented and identify the smallest safe edit surface.
Do not edit files. Continue local non-overlapping work while it runs.
Return relevant files, symbols, risks, and recommended next step.
```

### Build

```text
Use implementation-builder to implement <change>. You own <files/modules>.
Wait for this agent before editing the same files. Do not edit outside that scope unless required and reported.
Run the narrowest cheap validation if available. Return files changed, behavior implemented, and validation result.
```

### Test

```text
Use test-author to add focused tests for <behavior>. You own <test files or package>.
Avoid live services, credentials, wall-clock dependence, and network calls unless the existing harness already mocks them.
Wait if implementation depends on these tests; otherwise continue local non-overlapping work.
Return test files changed, behaviors covered, and the next focused command.
```

### Verify

```text
Use verification-engineer to validate <change or package>. Prefer focused commands first.
If a failure appears unrelated or environment-specific, report that separately. Do not fix unrelated failures.
Wait for this result before final handoff. Return exact commands, outcomes, and the smallest next validation step.
```

### Docs

```text
Use docs-maintainer to update docs for <changed behavior>. Preserve existing structure and terminology.
Only edit documentation made stale by this change.
Continue local non-overlapping work while it runs. Return files changed and semantic docs changes.
```

### Review

```text
Use quality-reviewer to review the current patch for correctness, regressions, security, performance, and missing validation.
Report findings first with file/line references. If no issues are found, say so and list residual test gaps.
Wait for this result before final handoff.
```

## Integration

When subagents return:

- Resolve conflicting findings against local evidence.
- Do not paste full subagent transcripts into the final answer.
- Report changed files, behavior delivered, validation run, unresolved risks, and the next focused command if useful.

## Cost Controls

- Use `$fast-dev` first when a task might be small.
- Spawn fewer agents with tighter, stable prompt templates before increasing fan-out.
- Prefer read-only researchers and reviewers for parallel context gathering.
- Avoid broad validation and broad internet research unless requested or justified by risk.
- Close completed agents once their results have been integrated.

## Runtime Controls

- Subagents inherit the parent session sandbox and approval behavior.
- Read-only custom agents should still declare `sandbox_mode = "read-only"` as a local default.
- Keep write-capable implementation, test, and docs agents un-sandboxed in the template so they inherit the parent session's current project permissions.
- In interactive sessions, approval prompts can surface from inactive agent threads; inspect the source thread before approving risky actions.
- In non-interactive runs, actions that need unavailable approval can fail and return that failure to the parent workflow.
- For cost control, prefer `[agents] max_threads = 4`, `max_depth = 1`, and bounded `job_max_runtime_seconds` in user or project config.

## Model Defaults

- Use `gpt-5.5` for demanding planning, implementation, and independent review.
- Use `gpt-5.4-mini` for read-heavy scans, docs, focused tests, validation triage, and summarization.
- Use `model_reasoning_effort = "high"` only for complex logic, edge-case tracing, security review, or high-risk review.
- Use `model_reasoning_effort = "low"` for straightforward docs or summarization where speed matters most.
