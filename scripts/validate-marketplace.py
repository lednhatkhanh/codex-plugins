#!/usr/bin/env python3
"""Validate the personal Codex plugin marketplace without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any


SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_MANIFEST_KEYS = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "hooks",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
ALLOWED_INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
ALLOWED_AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
ALLOWED_REASONING_EFFORTS = {"minimal", "low", "medium", "high"}
MAX_SKILL_DESCRIPTION_LENGTH = 220
MAX_DEFAULT_PROMPTS = 3
MAX_DEFAULT_PROMPT_LENGTH = 128


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", help="Validate one plugin directory instead of the whole marketplace")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    if args.plugin:
        validate_plugin(Path(args.plugin).resolve(), errors)
    else:
        validate_marketplace(repo_root, errors)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    target = args.plugin if args.plugin else repo_root / ".agents" / "plugins" / "marketplace.json"
    print(f"Validation passed: {target}")
    return 0


def validate_marketplace(repo_root: Path, errors: list[str]) -> None:
    marketplace_path = repo_root / ".agents" / "plugins" / "marketplace.json"
    marketplace = load_json_object(marketplace_path, errors)
    if marketplace is None:
        return

    require_string(marketplace, "name", "marketplace.name", errors)
    interface = marketplace.get("interface")
    if not isinstance(interface, dict):
        errors.append("marketplace.interface must be an object")
    else:
        require_string(interface, "displayName", "marketplace.interface.displayName", errors)

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append("marketplace.plugins must be an array")
        return

    seen: set[str] = set()
    for index, entry in enumerate(plugins):
        prefix = f"marketplace.plugins[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue

        name = require_string(entry, "name", f"{prefix}.name", errors)
        if name and name in seen:
            errors.append(f"{prefix}.name duplicates plugin {name}")
        if name:
            seen.add(name)
            validate_name(name, f"{prefix}.name", errors)

        source = entry.get("source")
        plugin_root: Path | None = None
        if isinstance(source, str):
            plugin_root = resolve_marketplace_path(repo_root, source, f"{prefix}.source", errors)
            if name and source != f"./plugins/{name}":
                errors.append(f"{prefix}.source must be ./plugins/{name}")
        elif not isinstance(source, dict):
            errors.append(f"{prefix}.source must be an object or ./ path string")
        else:
            if source.get("source") != "local":
                errors.append(f"{prefix}.source.source must be local")
            raw_path = require_string(source, "path", f"{prefix}.source.path", errors)
            if raw_path:
                plugin_root = resolve_marketplace_path(repo_root, raw_path, f"{prefix}.source.path", errors)
                if name and raw_path != f"./plugins/{name}":
                    errors.append(f"{prefix}.source.path must be ./plugins/{name}")

        policy = entry.get("policy")
        if not isinstance(policy, dict):
            errors.append(f"{prefix}.policy must be an object")
        else:
            installation = require_string(policy, "installation", f"{prefix}.policy.installation", errors)
            authentication = require_string(policy, "authentication", f"{prefix}.policy.authentication", errors)
            if installation and installation not in ALLOWED_INSTALL_POLICIES:
                errors.append(f"{prefix}.policy.installation has unsupported value {installation}")
            if authentication and authentication not in ALLOWED_AUTH_POLICIES:
                errors.append(f"{prefix}.policy.authentication has unsupported value {authentication}")

        require_string(entry, "category", f"{prefix}.category", errors)

        if plugin_root:
            validate_plugin(plugin_root, errors, expected_name=name)

    validate_all_plugin_dirs_are_listed(repo_root, seen, errors)
    validate_no_top_level_skills(repo_root, errors)


def validate_plugin(plugin_root: Path, errors: list[str], expected_name: str | None = None) -> None:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = load_json_object(manifest_path, errors)
    if manifest is None:
        return

    reject_todo(manifest, f"{manifest_path}", errors)

    unknown = sorted(set(manifest) - ALLOWED_MANIFEST_KEYS)
    for key in unknown:
        errors.append(f"{manifest_path}: unsupported plugin.json field {key}")

    name = require_string(manifest, "name", f"{manifest_path}: name", errors)
    if name:
        validate_name(name, f"{manifest_path}: name", errors)
    if expected_name and name != expected_name:
        errors.append(f"{manifest_path}: name must match marketplace entry {expected_name}")
    if name and plugin_root.name != name:
        errors.append(f"{manifest_path}: name must match folder name {plugin_root.name}")

    version = require_string(manifest, "version", f"{manifest_path}: version", errors)
    if version and SEMVER_RE.fullmatch(version) is None:
        errors.append(f"{manifest_path}: version must be strict semver")
    require_string(manifest, "description", f"{manifest_path}: description", errors)

    author = manifest.get("author")
    if not isinstance(author, dict):
        errors.append(f"{manifest_path}: author must be an object")
    else:
        require_string(author, "name", f"{manifest_path}: author.name", errors)

    skills_path = manifest.get("skills")
    if skills_path is not None:
        validate_relative_path(plugin_root, skills_path, "skills", f"{manifest_path}: skills", errors)
        validate_skills(plugin_root / "skills", errors)

    if manifest.get("apps") is not None:
        validate_relative_path(plugin_root, manifest["apps"], ".app.json", f"{manifest_path}: apps", errors)
    if manifest.get("mcpServers") is not None:
        validate_relative_path(
            plugin_root,
            manifest["mcpServers"],
            ".mcp.json",
            f"{manifest_path}: mcpServers",
            errors,
        )
    hooks_path = manifest.get("hooks")
    if hooks_path is not None:
        validate_hooks(plugin_root, hooks_path, f"{manifest_path}: hooks", errors)
    default_hooks_path = plugin_root / "hooks" / "hooks.json"
    if default_hooks_path.exists():
        load_json_object(default_hooks_path, errors)

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{manifest_path}: interface must be an object")
    else:
        for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            require_string(interface, field, f"{manifest_path}: interface.{field}", errors)
        default_prompt = interface.get("defaultPrompt", interface.get("default_prompt"))
        if default_prompt is None:
            errors.append(f"{manifest_path}: interface.defaultPrompt is required")
        else:
            validate_default_prompt(default_prompt, f"{manifest_path}: interface.defaultPrompt", errors)
        capabilities = interface.get("capabilities")
        if not isinstance(capabilities, list) or not all(isinstance(item, str) and item for item in capabilities):
            errors.append(f"{manifest_path}: interface.capabilities must be an array of strings")

    validate_agent_templates(plugin_root, errors)
    validate_prompt_templates(plugin_root, errors)


def validate_skills(skills_root: Path, errors: list[str]) -> None:
    if not skills_root.is_dir():
        errors.append(f"{skills_root}: skills directory does not exist")
        return
    for skill_path in sorted(skills_root.glob("*/SKILL.md")):
        text = read_text(skill_path, errors)
        if text is None:
            continue
        reject_todo(text, str(skill_path), errors)
        frontmatter = parse_frontmatter(text, skill_path, errors)
        if frontmatter is None:
            continue
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{skill_path}: frontmatter.name is required")
        elif skill_path.parent.name != name:
            errors.append(f"{skill_path}: frontmatter.name must match folder name {skill_path.parent.name}")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{skill_path}: frontmatter.description is required")
        elif len(description) > MAX_SKILL_DESCRIPTION_LENGTH:
            errors.append(
                f"{skill_path}: frontmatter.description should stay under "
                f"{MAX_SKILL_DESCRIPTION_LENGTH} chars for skill-list context budget"
            )


def validate_agent_templates(plugin_root: Path, errors: list[str]) -> None:
    agents_root = plugin_root / "assets" / "agents"
    if not agents_root.exists():
        return
    for path in sorted(agents_root.glob("*.toml")):
        try:
            with path.open("rb") as handle:
                payload = tomllib.load(handle)
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{path}: invalid TOML: {exc}")
            continue
        for field in ("name", "description", "developer_instructions"):
            value = payload.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{path}: missing non-empty {field}")
        name = payload.get("name")
        if isinstance(name, str):
            if path.stem != name:
                errors.append(f"{path}: filename should match agent name {name}")
            validate_name(name, f"{path}: name", errors)
        reasoning_effort = payload.get("model_reasoning_effort")
        if reasoning_effort is not None and reasoning_effort not in ALLOWED_REASONING_EFFORTS:
            errors.append(f"{path}: model_reasoning_effort has unsupported value {reasoning_effort}")
        sandbox_mode = payload.get("sandbox_mode")
        if sandbox_mode is not None and sandbox_mode not in {"read-only", "workspace-write", "danger-full-access"}:
            errors.append(f"{path}: sandbox_mode has unsupported value {sandbox_mode}")
        nicknames = payload.get("nickname_candidates")
        if nicknames is not None:
            validate_nicknames(nicknames, path, errors)


def validate_prompt_templates(plugin_root: Path, errors: list[str]) -> None:
    prompts_root = plugin_root / "prompts"
    if not prompts_root.exists():
        return
    if not prompts_root.is_dir():
        errors.append(f"{prompts_root}: prompts must be a directory")
        return
    for path in sorted(prompts_root.glob("*.md")):
        validate_name(path.stem, f"{path}: prompt filename", errors)
        text = read_text(path, errors)
        if text is None:
            continue
        reject_todo(text, str(path), errors)
        if not text.strip():
            errors.append(f"{path}: prompt template must not be empty")
        if len(text) > 2000:
            errors.append(f"{path}: prompt template should stay compact")


def validate_hooks(plugin_root: Path, value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, str):
        validate_plugin_path(plugin_root, value, label, errors)
        return
    if isinstance(value, list):
        if not value:
            errors.append(f"{label} must not be an empty array")
            return
        for index, item in enumerate(value):
            validate_hooks(plugin_root, item, f"{label}[{index}]", errors)
        return
    if isinstance(value, dict):
        return
    errors.append(f"{label} must be a relative path, array, or inline hooks object")


def validate_all_plugin_dirs_are_listed(repo_root: Path, listed_names: set[str], errors: list[str]) -> None:
    plugins_root = repo_root / "plugins"
    if not plugins_root.exists():
        return
    for plugin_dir in sorted(path for path in plugins_root.iterdir() if path.is_dir()):
        if plugin_dir.name not in listed_names:
            errors.append(f"{plugin_dir}: plugin directory is not listed in marketplace.json")


def validate_no_top_level_skills(repo_root: Path, errors: list[str]) -> None:
    for skill_file in sorted(repo_root.glob("*/SKILL.md")):
        if skill_file.parts[-2] != "plugins":
            errors.append(f"{skill_file}: standalone top-level skills are not allowed in this marketplace")


def validate_default_prompt(value: Any, label: str, errors: list[str]) -> None:
    prompts = value if isinstance(value, list) else [value]
    if not all(isinstance(item, str) and item.strip() for item in prompts):
        errors.append(f"{label} must be a string or array of non-empty strings")
        return
    if len(prompts) > MAX_DEFAULT_PROMPTS:
        errors.append(f"{label} must include at most {MAX_DEFAULT_PROMPTS} prompts")
    for index, prompt in enumerate(prompts):
        if len(prompt) > MAX_DEFAULT_PROMPT_LENGTH:
            errors.append(f"{label}[{index}] must stay under {MAX_DEFAULT_PROMPT_LENGTH} chars")


def validate_nicknames(value: Any, path: Path, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{path}: nickname_candidates must be a non-empty list")
        return
    seen: set[str] = set()
    for nickname in value:
        if not isinstance(nickname, str) or not nickname.strip():
            errors.append(f"{path}: nickname_candidates must contain non-empty strings")
            continue
        if nickname in seen:
            errors.append(f"{path}: nickname_candidates contains duplicate {nickname}")
        seen.add(nickname)
        if not re.fullmatch(r"[A-Za-z0-9 _-]+", nickname):
            errors.append(f"{path}: nickname {nickname!r} uses unsupported characters")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"{path}: missing JSON file")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path}: must contain a JSON object")
        return None
    return payload


def read_text(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
        return None


def parse_frontmatter(text: str, path: Path, errors: list[str]) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        errors.append(f"{path}: missing YAML frontmatter")
        return None
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{path}: unterminated YAML frontmatter")
        return None
    payload: dict[str, str] = {}
    for line in text[4:end].splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            errors.append(f"{path}: unsupported frontmatter line {line!r}")
            continue
        key, value = stripped.split(":", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        payload[key.strip()] = value
    return payload


def require_string(payload: dict[str, Any], key: str, label: str, errors: list[str]) -> str | None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return None
    return value


def validate_name(name: str, label: str, errors: list[str]) -> None:
    if NAME_RE.fullmatch(name) is None:
        errors.append(f"{label} must be lowercase hyphen-case")


def reject_todo(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, str):
        if "[TODO:" in value:
            errors.append(f"{label}: contains [TODO: ...] placeholder")
    elif isinstance(value, list):
        for item in value:
            reject_todo(item, label, errors)
    elif isinstance(value, dict):
        for item in value.values():
            reject_todo(item, label, errors)


def resolve_marketplace_path(repo_root: Path, raw_path: str, label: str, errors: list[str]) -> Path | None:
    posix = PurePosixPath(raw_path)
    if not raw_path.startswith("./") or ".." in posix.parts:
        errors.append(f"{label} must start with ./ and stay inside the repo")
        return None
    path = (repo_root / raw_path[2:]).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError:
        errors.append(f"{label} resolves outside the repo")
        return None
    if not path.is_dir():
        errors.append(f"{label} points to missing plugin directory {path}")
        return None
    return path


def validate_relative_path(plugin_root: Path, raw_path: Any, expected_name: str, label: str, errors: list[str]) -> None:
    if not isinstance(raw_path, str) or not raw_path.startswith("./") or ".." in PurePosixPath(raw_path).parts:
        errors.append(f"{label} must be a relative ./ path")
        return
    path = plugin_root / raw_path[2:]
    if path.name != expected_name:
        errors.append(f"{label} should point to {expected_name}")
    if not path.exists():
        errors.append(f"{label} points to missing path {path}")


def validate_plugin_path(plugin_root: Path, raw_path: Any, label: str, errors: list[str]) -> None:
    if not isinstance(raw_path, str) or not raw_path.startswith("./") or ".." in PurePosixPath(raw_path).parts:
        errors.append(f"{label} must be a relative ./ path")
        return
    path = (plugin_root / raw_path[2:]).resolve()
    try:
        path.relative_to(plugin_root.resolve())
    except ValueError:
        errors.append(f"{label} resolves outside the plugin")
        return
    if not path.exists():
        errors.append(f"{label} points to missing path {path}")


if __name__ == "__main__":
    sys.exit(main())
