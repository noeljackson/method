"""Shared validation and context-loading helpers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "dist" / "pack"
CONTEXT_SOURCE = ROOT / "src" / "context.json"
CONTEXT_KEYS = ("program", "experiment", "secrets")


class DataError(ValueError):
    """A user-facing structured-data error."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        try:
            label = path.relative_to(ROOT)
        except ValueError:
            label = path
        raise DataError(f"{label}: cannot read: {error}") from None
    except json.JSONDecodeError as error:
        try:
            label = path.relative_to(ROOT)
        except ValueError:
            label = path
        raise DataError(
            f"{label}:{error.lineno}:{error.colno}: invalid JSON: {error.msg}"
        ) from None


def context_spec() -> dict[str, Any]:
    raw = read_json(CONTEXT_SOURCE)
    expected = {
        "schema_version", "base_modules", "module_order",
        "profile_requirement", "flags",
    }
    if not isinstance(raw, dict) or set(raw) != expected:
        raise DataError(f"src/context.json: fields must be {sorted(expected)}")
    if raw["schema_version"] != 1:
        raise DataError("src/context.json: schema_version must be 1")
    for field in ("base_modules", "module_order"):
        values = raw[field]
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(value, str) and value for value in values)
            or len(values) != len(set(values))
        ):
            raise DataError(f"src/context.json: {field} must be a unique string array")
    if raw["base_modules"] != ["BASE.md"]:
        raise DataError("src/context.json: BASE.md must be the only base module")
    profile = raw["profile_requirement"]
    if (
        not isinstance(profile, dict)
        or set(profile) != {"normal", "missing_or_invalid"}
        or not all(isinstance(value, str) and value for value in profile.values())
    ):
        raise DataError("src/context.json: invalid profile_requirement")
    flags = raw["flags"]
    if not isinstance(flags, dict) or tuple(flags) != CONTEXT_KEYS:
        raise DataError(f"src/context.json: flags must be ordered as {CONTEXT_KEYS}")
    modules: list[str] = []
    for key in CONTEXT_KEYS:
        value = flags[key]
        if (
            not isinstance(value, dict)
            or set(value) != {"module", "activate_when"}
            or not all(isinstance(item, str) and item for item in value.values())
        ):
            raise DataError(f"src/context.json: flags.{key} is invalid")
        modules.append(value["module"])
    if modules != raw["module_order"]:
        raise DataError("src/context.json: flag modules must equal module_order")
    return raw


def validate_context_flags(value: object) -> dict[str, bool]:
    """Validate the exact non-authoritative ContextFlags shape."""
    if not isinstance(value, dict) or set(value) != set(CONTEXT_KEYS):
        raise DataError(f"ContextFlags fields must be exactly {CONTEXT_KEYS}")
    if not all(isinstance(value[key], bool) for key in CONTEXT_KEYS):
        raise DataError("ContextFlags values must be boolean")
    return {key: value[key] for key in CONTEXT_KEYS}


def empty_context_flags() -> dict[str, bool]:
    return {key: False for key in CONTEXT_KEYS}


def merge_context_flags(*values: object) -> dict[str, bool]:
    """OR caller, profile, and model flags; no source can clear another."""
    merged = empty_context_flags()
    for value in values:
        checked = validate_context_flags(value)
        for key in CONTEXT_KEYS:
            merged[key] = merged[key] or checked[key]
    return merged


def resolve_context_modules(
    value: object, spec: dict[str, Any] | None = None
) -> list[str]:
    spec = spec or context_spec()
    flags = validate_context_flags(value)
    return [spec["flags"][key]["module"] for key in CONTEXT_KEYS if flags[key]]


def validate_module_name(module: object, allowed: set[str]) -> str:
    if not isinstance(module, str) or not module:
        raise DataError("module names must be non-empty strings")
    pure = PurePosixPath(module)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != module:
        raise DataError(f"unsafe modular-pack path: {module}")
    if module not in allowed:
        raise DataError(f"module is not allowed by the context manifest: {module}")
    path = PACK / module
    if path.is_symlink() or any(
        parent.is_symlink() for parent in path.parents if parent != PACK.parent
    ):
        raise DataError(f"modular-pack path may not traverse a symlink: {module}")
    resolved_pack = PACK.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(resolved_pack) or not resolved.is_file():
        raise DataError(f"modular-pack path is not a regular contained file: {module}")
    return module


def validate_module_list(value: object, allowed: set[str]) -> list[str]:
    if not isinstance(value, list):
        raise DataError("modules must be an array")
    modules = [validate_module_name(module, allowed) for module in value]
    if len(modules) != len(set(modules)):
        raise DataError("modules must be unique")
    return modules


def allowed_context_modules(spec: dict[str, Any] | None = None) -> set[str]:
    """Return protocol modules only when every one is manifest-listed."""
    spec = spec or context_spec()
    manifest = read_json(PACK / "MANIFEST.json")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise DataError("dist/pack/MANIFEST.json: files must be an array")
    paths: list[str] = []
    for item in manifest["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise DataError("dist/pack/MANIFEST.json: invalid file entry")
        paths.append(item["path"])
    if len(paths) != len(set(paths)):
        raise DataError("dist/pack/MANIFEST.json: duplicate file entries")
    routeable = set(spec["module_order"])
    missing = routeable - set(paths)
    if missing:
        raise DataError(
            "context modules missing from the generated manifest: "
            + ", ".join(sorted(missing))
        )
    return routeable


def profile_payload(text: str) -> str:
    """Return the exact profile bytes covered by the acceptance digest."""
    output: list[str] = []
    skipping = False
    for line in text.splitlines(keepends=True):
        if line == "## Acceptance\n":
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            output.append(line)
    return "".join(output)


def profile_metadata(text: str) -> dict[str, str]:
    labels = {
        "Profile status": "status",
        "Authority source": "authority_source",
        "Profile digest": "profile_digest",
        "Accepted by": "accepted_by",
        "Accepted at": "accepted_at",
        "Acceptance receipt": "receipt",
    }
    metadata: dict[str, str] = {}
    for label, key in labels.items():
        match = re.search(rf"^- {re.escape(label)}: `([^`]+)`$", text, re.MULTILINE)
        if match:
            metadata[key] = match.group(1)
    return metadata


def validate_accepted_profile(
    text: str,
    profile_id: str,
    authorities: object,
) -> dict[str, str]:
    metadata = profile_metadata(text)
    required = {
        "status", "authority_source", "profile_digest", "accepted_by",
        "accepted_at", "receipt",
    }
    if set(metadata) != required:
        raise DataError(f"profile {profile_id}: incomplete acceptance metadata")
    if metadata["status"] != "ACCEPTED":
        raise DataError(f"profile {profile_id}: status must be ACCEPTED")
    digest = hashlib.sha256(profile_payload(text).encode()).hexdigest()
    if metadata["profile_digest"] != digest:
        raise DataError(f"profile {profile_id}: acceptance digest is stale")
    if not isinstance(authorities, dict):
        raise DataError("fixture authorities must be an object")
    expected = {
        "profile": profile_id,
        "authority_source": metadata["authority_source"],
        "accepted_by": metadata["accepted_by"],
        "accepted_at": metadata["accepted_at"],
        "profile_digest": digest,
    }
    if authorities.get(metadata["receipt"]) != expected:
        raise DataError(f"profile {profile_id}: authority receipt does not match")
    return metadata
