#!/usr/bin/env python3
"""Noel Method v0.4 policy verification and permissions resolver."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
PACKAGED = (
    (SCRIPT_ROOT / "CONTEXT.json").is_file()
    and (SCRIPT_ROOT / "KERNEL.md").is_file()
)
ROOT = SCRIPT_ROOT
PACK = ROOT if PACKAGED else ROOT / "dist" / "pack"
CONTEXT_SOURCE = ROOT / "CONTEXT.json" if PACKAGED else ROOT / "src" / "context.json"
PROTOCOL_KEYS = ("program", "experiment", "secrets")
PROJECT_POLICY_FIELDS = {
    "schema_version", "method_version", "policy_id", "policy", "acceptance"
}
POLICY_FIELDS = {
    "scope", "canonical_sources", "actions", "protocols", "gates", "secrets",
    "program", "reporting",
}
SECRET_FIELDS = {
    "routine_access", "approved_references", "delivery", "artifact_scan",
    "exposure_response", "forensic_quarantine", "clean_context",
    "encrypted_envelopes",
}
AUTHORITY_RECEIPT_FIELDS = {
    "policy_id", "method_version", "policy_sha256", "authority_source",
    "accepted_by", "accepted_at",
}
TASK_FIELDS = {
    "schema_version", "task_id", "outcome", "scope", "resource_refs",
    "requested_actions", "forbidden_actions", "signals", "required_gates",
    "baseline_identity", "stop_conditions", "expires_on",
}
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
POLICY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
METHOD_VERSION_RE = re.compile(r"^0\.4\.[0-9]+$")
HEX_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


class DataError(ValueError):
    """A user-facing structured-data error."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DataError(f"duplicate JSON field: {key}")
        value[key] = item
    return value


def _reject_nonfinite(value: str) -> object:
    raise DataError(f"non-finite JSON number is forbidden: {value}")


def read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except OSError as error:
        raise DataError(f"{path}: cannot read: {error}") from None
    except json.JSONDecodeError as error:
        raise DataError(
            f"{path}:{error.lineno}:{error.colno}: invalid JSON: {error.msg}"
        ) from None


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _object(value: object, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise DataError(f"{label}: fields must be exactly {sorted(fields)}")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DataError(f"{label}: must be non-empty text")
    return value


def _identifier(value: object, label: str, *, policy: bool = False) -> str:
    text = _text(value, label)
    pattern = POLICY_ID_RE if policy else IDENTIFIER_RE
    if not pattern.fullmatch(text):
        raise DataError(f"{label}: invalid identifier")
    return text


def _strings(
    value: object, label: str, *, allow_empty: bool = False
) -> list[str]:
    if not isinstance(value, list):
        raise DataError(f"{label}: must be an array")
    if not allow_empty and not value:
        raise DataError(f"{label}: must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise DataError(f"{label}: entries must be non-empty text")
    if len(value) != len(set(value)):
        raise DataError(f"{label}: entries must be unique")
    return list(value)


def _safe_module_path(module: object) -> str:
    if not isinstance(module, str) or not module:
        raise DataError("module names must be non-empty strings")
    pure = PurePosixPath(module)
    if (
        pure.is_absolute()
        or ".." in pure.parts
        or str(pure) != module
        or pure.suffix != ".md"
    ):
        raise DataError(f"unsafe modular-pack path: {module}")
    return module


def installed_method_version() -> str:
    version_file = ROOT / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    context = read_json(ROOT / "CONTEXT.json")
    if not isinstance(context, dict):
        raise DataError("installed CONTEXT.json must be an object")
    return _text(context.get("version"), "installed method version")


def context_spec() -> dict[str, Any]:
    raw = read_json(CONTEXT_SOURCE)
    fields = {
        "schema_version", "kernel", "module_order", "protocols",
        "authority_modes", "resolved_mode",
    }
    if PACKAGED:
        packaged_fields = fields | {"method", "version"}
        value = _object(raw, packaged_fields, "CONTEXT.json")
        _text(value["method"], "CONTEXT.json.method")
        _text(value["version"], "CONTEXT.json.version")
        raw = {field: value[field] for field in fields}
    spec = _object(raw, fields, "src/context.json")
    if spec["schema_version"] != 3:
        raise DataError("src/context.json: schema_version must be 3")
    if spec["kernel"] != "KERNEL.md":
        raise DataError("src/context.json: kernel must be KERNEL.md")
    module_order = _strings(spec["module_order"], "src/context.json.module_order")
    protocols = _object(
        spec["protocols"], set(PROTOCOL_KEYS), "src/context.json.protocols"
    )
    modules: list[str] = []
    for key in PROTOCOL_KEYS:
        item = _object(
            protocols[key], {"module", "task_signal"},
            f"src/context.json.protocols.{key}",
        )
        modules.append(_safe_module_path(item["module"]))
        _text(item["task_signal"], f"protocols.{key}.task_signal")
    if modules != module_order:
        raise DataError("src/context.json: module_order and protocols differ")
    expected_modules = [f"protocols/{key}.md" for key in PROTOCOL_KEYS]
    if modules != expected_modules:
        raise DataError(
            f"src/context.json: protocol modules must be {expected_modules}"
        )
    modes = _object(
        spec["authority_modes"],
        {"default", "direct", "resolved"},
        "src/context.json.authority_modes",
    )
    if modes["default"] != "direct":
        raise DataError("src/context.json: direct must be the default authority mode")
    direct = _object(
        modes["direct"], {"requires"}, "src/context.json.authority_modes.direct"
    )
    if direct["requires"] != []:
        raise DataError("src/context.json: direct mode requires no Method artifacts")
    resolved = _object(
        modes["resolved"],
        {"selection", "requires"},
        "src/context.json.authority_modes.resolved",
    )
    if resolved["selection"] != "explicit":
        raise DataError("src/context.json: resolved mode selection must be explicit")
    if resolved["requires"] != ["TaskRequest", "ResolvedPermissions"]:
        raise DataError("src/context.json: resolved mode requirements differ")
    _object(
        spec["resolved_mode"],
        {
            "policy_schema", "authorities_schema", "task_schema",
            "permissions_schema", "program_schema", "resolver",
        },
        "src/context.json.resolved_mode",
    )
    return spec


def validate_protocol_flags(value: object) -> dict[str, bool]:
    flags = _object(value, set(PROTOCOL_KEYS), "protocol flags")
    if not all(isinstance(flags[key], bool) for key in PROTOCOL_KEYS):
        raise DataError("protocol flags must be boolean")
    return {key: flags[key] for key in PROTOCOL_KEYS}


def resolve_context_modules(
    protocols: list[str], spec: dict[str, Any] | None = None
) -> list[str]:
    spec = spec or context_spec()
    if (
        not isinstance(protocols, list)
        or len(protocols) != len(set(protocols))
        or any(item not in PROTOCOL_KEYS for item in protocols)
    ):
        raise DataError("protocols must be a unique array of known protocol names")
    selected = set(protocols)
    try:
        return [
            _safe_module_path(spec["protocols"][key]["module"])
            for key in PROTOCOL_KEYS
            if key in selected
        ]
    except (KeyError, TypeError) as error:
        raise DataError(f"malformed context specification: {error}") from None


def validate_module_name(module: object, allowed: set[str]) -> str:
    module = _safe_module_path(module)
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


def allowed_context_modules(spec: dict[str, Any] | None = None) -> set[str]:
    spec = spec or context_spec()
    return set(spec["module_order"])


def _validate_method_version(value: object, supported: str) -> str:
    version = _text(value, "policy.method_version")
    if not METHOD_VERSION_RE.fullmatch(version):
        raise DataError("policy.method_version: expected a 0.4.x release")
    if not METHOD_VERSION_RE.fullmatch(supported):
        raise DataError(f"installed method version is unsupported: {supported}")
    return version


def validate_policy(policy: object) -> dict[str, Any]:
    value = _object(policy, POLICY_FIELDS, "ProjectPolicy.policy")
    _strings(value["scope"], "ProjectPolicy.policy.scope")

    sources = value["canonical_sources"]
    if not isinstance(sources, list) or not sources:
        raise DataError(
            "ProjectPolicy.policy.canonical_sources: must be a non-empty array"
        )
    source_ids: list[str] = []
    precedences: list[int] = []
    for index, source in enumerate(sources):
        item = _object(
            source, {"id", "owns", "precedence"},
            f"ProjectPolicy.policy.canonical_sources[{index}]",
        )
        source_ids.append(_identifier(item["id"], f"canonical_sources[{index}].id"))
        _text(item["owns"], f"canonical_sources[{index}].owns")
        if not isinstance(item["precedence"], int) or isinstance(item["precedence"], bool):
            raise DataError(f"canonical_sources[{index}].precedence: must be an integer")
        precedences.append(item["precedence"])
    if len(source_ids) != len(set(source_ids)):
        raise DataError("ProjectPolicy.policy.canonical_sources: IDs must be unique")
    if sorted(precedences) != list(range(1, len(precedences) + 1)):
        raise DataError(
            "ProjectPolicy.policy.canonical_sources: precedence must be contiguous"
        )

    actions = _object(
        value["actions"], {"allowed", "forbidden"}, "ProjectPolicy.policy.actions"
    )
    allowed = _strings(
        actions["allowed"], "ProjectPolicy.policy.actions.allowed", allow_empty=True
    )
    forbidden = _strings(
        actions["forbidden"],
        "ProjectPolicy.policy.actions.forbidden",
        allow_empty=True,
    )
    overlap = set(allowed) & set(forbidden)
    if overlap:
        raise DataError(
            "ProjectPolicy.policy.actions: allowed and forbidden overlap: "
            + ", ".join(sorted(overlap))
        )

    validate_protocol_flags(value["protocols"])

    gates = value["gates"]
    if not isinstance(gates, list) or not gates:
        raise DataError("ProjectPolicy.policy.gates: must be a non-empty array")
    gate_ids: list[str] = []
    for index, gate in enumerate(gates):
        item = _object(
            gate, {"id", "default", "before", "required_evidence"},
            f"ProjectPolicy.policy.gates[{index}]",
        )
        gate_ids.append(_identifier(item["id"], f"gates[{index}].id"))
        if not isinstance(item["default"], bool):
            raise DataError(f"gates[{index}].default: must be boolean")
        _text(item["before"], f"gates[{index}].before")
        _text(item["required_evidence"], f"gates[{index}].required_evidence")
    if len(gate_ids) != len(set(gate_ids)):
        raise DataError("ProjectPolicy.policy.gates: IDs must be unique")

    secrets = _object(
        value["secrets"], SECRET_FIELDS, "ProjectPolicy.policy.secrets"
    )
    _strings(
        secrets["approved_references"],
        "ProjectPolicy.policy.secrets.approved_references",
    )
    for field in SECRET_FIELDS - {"approved_references"}:
        _text(secrets[field], f"ProjectPolicy.policy.secrets.{field}")

    program = _object(
        value["program"],
        {"trigger", "repair_authority"},
        "ProjectPolicy.policy.program",
    )
    _text(program["trigger"], "ProjectPolicy.policy.program.trigger")
    _text(
        program["repair_authority"],
        "ProjectPolicy.policy.program.repair_authority",
    )
    _text(value["reporting"], "ProjectPolicy.policy.reporting")
    return value


def project_policy_payload(project_policy: object) -> bytes:
    value = _object(project_policy, PROJECT_POLICY_FIELDS, "ProjectPolicy")
    validate_policy(value["policy"])
    payload = {
        "schema_version": value["schema_version"],
        "method_version": value["method_version"],
        "policy_id": value["policy_id"],
        "policy": value["policy"],
    }
    return canonical_json(payload)


def project_policy_digest(project_policy: object) -> str:
    return hashlib.sha256(project_policy_payload(project_policy)).hexdigest()


def validate_authority_registry(authorities: object) -> dict[str, Any]:
    if not isinstance(authorities, dict):
        raise DataError("authority receipts must be an object")
    for receipt, raw in authorities.items():
        _identifier(receipt, "authority receipt id")
        item = _object(
            raw, AUTHORITY_RECEIPT_FIELDS, f"authority receipt {receipt}"
        )
        _identifier(item["policy_id"], f"{receipt}.policy_id", policy=True)
        if not METHOD_VERSION_RE.fullmatch(_text(
            item["method_version"], f"{receipt}.method_version"
        )):
            raise DataError(f"{receipt}.method_version: expected a 0.4.x release")
        digest = _text(item["policy_sha256"], f"{receipt}.policy_sha256")
        if not HEX_DIGEST_RE.fullmatch(digest):
            raise DataError(f"{receipt}.policy_sha256: expected lowercase SHA-256")
        for field in ("authority_source", "accepted_by", "accepted_at"):
            _text(item[field], f"{receipt}.{field}")
    return authorities


def validate_project_policy(
    project_policy: object,
    authorities: object,
    *,
    supported_version: str | None = None,
    require_accepted: bool = True,
) -> dict[str, Any]:
    value = _object(project_policy, PROJECT_POLICY_FIELDS, "ProjectPolicy")
    if value["schema_version"] != 1:
        raise DataError("ProjectPolicy.schema_version: must be 1")
    supported = supported_version or installed_method_version()
    version = _validate_method_version(value["method_version"], supported)
    policy_id = _identifier(
        value["policy_id"], "ProjectPolicy.policy_id", policy=True
    )
    policy = validate_policy(value["policy"])
    acceptance = _object(
        value["acceptance"],
        {
            "status", "policy_sha256", "authority_source", "accepted_by",
            "accepted_at", "receipt",
        },
        "ProjectPolicy.acceptance",
    )
    if not require_accepted:
        if acceptance["status"] not in {"draft", "accepted"}:
            raise DataError("ProjectPolicy.acceptance.status: invalid value")
        return {
            "policy_id": policy_id,
            "method_version": version,
            "policy_sha256": project_policy_digest(value),
            "policy": policy,
            "accepted": False,
        }
    if acceptance["status"] != "accepted":
        raise DataError("ProjectPolicy.acceptance.status: must be accepted")
    digest = project_policy_digest(value)
    if not HEX_DIGEST_RE.fullmatch(str(acceptance["policy_sha256"])):
        raise DataError(
            "ProjectPolicy.acceptance.policy_sha256: must be lowercase SHA-256"
        )
    if acceptance["policy_sha256"] != digest:
        raise DataError("ProjectPolicy acceptance digest is stale")
    for field in ("authority_source", "accepted_by", "accepted_at", "receipt"):
        _text(acceptance[field], f"ProjectPolicy.acceptance.{field}")
    checked_authorities = validate_authority_registry(authorities)
    expected = {
        "policy_id": policy_id,
        "method_version": version,
        "policy_sha256": digest,
        "authority_source": acceptance["authority_source"],
        "accepted_by": acceptance["accepted_by"],
        "accepted_at": acceptance["accepted_at"],
    }
    if checked_authorities.get(acceptance["receipt"]) != expected:
        raise DataError("ProjectPolicy authority receipt does not match")
    return {
        "policy_id": policy_id,
        "method_version": version,
        "policy_sha256": digest,
        "acceptance_receipt": acceptance["receipt"],
        "policy": policy,
        "accepted": True,
    }


def validate_task_request(task: object) -> dict[str, Any]:
    value = _object(task, TASK_FIELDS, "task")
    if value["schema_version"] != 1:
        raise DataError("task.schema_version: must be 1")
    _identifier(value["task_id"], "task.task_id")
    _text(value["outcome"], "task.outcome")
    scope = _object(value["scope"], {"include", "exclude"}, "task.scope")
    _strings(scope["include"], "task.scope.include")
    _strings(scope["exclude"], "task.scope.exclude", allow_empty=True)
    _strings(value["resource_refs"], "task.resource_refs", allow_empty=True)
    _strings(value["requested_actions"], "task.requested_actions", allow_empty=True)
    _strings(value["forbidden_actions"], "task.forbidden_actions", allow_empty=True)
    signals = _object(
        value["signals"],
        {"persistent_program", "controlled_comparison", "secret_risk"},
        "task.signals",
    )
    if not isinstance(signals["persistent_program"], bool):
        raise DataError("task.signals.persistent_program: must be boolean")
    if not isinstance(signals["controlled_comparison"], bool):
        raise DataError("task.signals.controlled_comparison: must be boolean")
    if signals["secret_risk"] not in {"none", "possible", "required"}:
        raise DataError("task.signals.secret_risk: invalid value")
    _strings(value["required_gates"], "task.required_gates", allow_empty=True)
    _text(value["baseline_identity"], "task.baseline_identity")
    _strings(value["stop_conditions"], "task.stop_conditions")
    _strings(value["expires_on"], "task.expires_on")
    return value


def resolve_permissions(
    project_policy: object,
    authorities: object,
    task: object,
    model_flags: object | None = None,
    *,
    supported_version: str | None = None,
) -> dict[str, Any]:
    checked_policy = validate_project_policy(
        project_policy, authorities, supported_version=supported_version
    )
    checked_task = validate_task_request(task)
    flags = validate_protocol_flags(
        model_flags
        if model_flags is not None
        else {key: False for key in PROTOCOL_KEYS}
    )
    policy = checked_policy["policy"]
    policy_flags = validate_protocol_flags(policy["protocols"])
    task_flags = {
        "program": checked_task["signals"]["persistent_program"],
        "experiment": checked_task["signals"]["controlled_comparison"],
        "secrets": checked_task["signals"]["secret_risk"] != "none",
    }
    protocols = [
        key
        for key in PROTOCOL_KEYS
        if policy_flags[key] or task_flags[key] or flags[key]
    ]
    if "program" in protocols and not any(
        reference.startswith("program-control:")
        for reference in checked_task["resource_refs"]
    ):
        raise DataError(
            "Program protocol requires a program-control: logical reference"
        )

    policy_allowed = list(policy["actions"]["allowed"])
    requested = list(checked_task["requested_actions"])
    unknown_actions = set(requested) - set(policy_allowed)
    if unknown_actions:
        raise DataError(
            "task requests actions not allowed by the ProjectPolicy: "
            + ", ".join(sorted(unknown_actions))
        )
    forbidden = list(dict.fromkeys(
        [*policy["actions"]["forbidden"], *checked_task["forbidden_actions"]]
    ))
    conflicts = set(requested) & set(forbidden)
    if conflicts:
        raise DataError(
            "task requests forbidden actions: " + ", ".join(sorted(conflicts))
        )

    gate_by_id = {gate["id"]: gate for gate in policy["gates"]}
    requested_gates = list(checked_task["required_gates"])
    unknown_gates = set(requested_gates) - set(gate_by_id)
    if unknown_gates:
        raise DataError(
            "task requests unknown gates: " + ", ".join(sorted(unknown_gates))
        )
    gate_ids = list(dict.fromkeys([
        *(gate["id"] for gate in policy["gates"] if gate["default"]),
        *requested_gates,
    ]))

    controls: dict[str, object] = {"reporting": policy["reporting"]}
    if "secrets" in protocols:
        controls["secrets"] = policy["secrets"]
    if "program" in protocols:
        controls["program_repair_authority"] = policy["program"]["repair_authority"]

    return {
        "schema_version": 1,
        "method_version": checked_policy["method_version"],
        "authority_mode": "resolved",
        "task_id": checked_task["task_id"],
        "task_sha256": hashlib.sha256(
            canonical_json(checked_task)
        ).hexdigest(),
        "policy_verified": True,
        "policy_ref": {
            "id": checked_policy["policy_id"],
            "policy_sha256": checked_policy["policy_sha256"],
            "acceptance_receipt": checked_policy["acceptance_receipt"],
        },
        "canonical_sources": sorted(
            policy["canonical_sources"], key=lambda item: item["precedence"]
        ),
        "allowed_actions": requested,
        "forbidden_actions": forbidden,
        "protocols": protocols,
        "required_gates": [gate_by_id[gate_id] for gate_id in gate_ids],
        "controls": controls,
    }


def validate_program_control(value: object) -> dict[str, Any]:
    fields = {
        "schema_version", "program", "state", "active_coordinates",
        "accepted_frontiers", "authorized_queue", "hard_gates", "forbidden_work",
        "reconciliation_receipt", "stop_condition", "resume_condition",
        "terminal_disposition",
    }
    control = _object(value, fields, "ProgramControl")
    if control["schema_version"] != 1:
        raise DataError("ProgramControl.schema_version: must be 1")
    _text(control["program"], "ProgramControl.program")
    if control["state"] not in {
        "ACTIVE", "STOPPED_FOR_REPLAN", "COMPLETE", "TERMINATED",
    }:
        raise DataError("ProgramControl.state: invalid state")
    for field in (
        "active_coordinates", "accepted_frontiers", "authorized_queue",
        "forbidden_work",
    ):
        if not isinstance(control[field], list):
            raise DataError(f"ProgramControl.{field}: must be an array")
    if not isinstance(control["hard_gates"], list):
        raise DataError("ProgramControl.hard_gates: must be an array")
    gate_ids: list[str] = []
    for index, raw_gate in enumerate(control["hard_gates"]):
        gate = _object(
            raw_gate,
            {"id", "state", "evidence_receipt"},
            f"ProgramControl.hard_gates[{index}]",
        )
        gate_ids.append(_identifier(gate["id"], f"hard_gates[{index}].id"))
        if gate["state"] not in {"SATISFIED", "UNSATISFIED"}:
            raise DataError(f"hard_gates[{index}].state: invalid state")
        receipt = gate["evidence_receipt"]
        if gate["state"] == "SATISFIED":
            if not isinstance(receipt, dict) or not receipt:
                raise DataError(
                    f"hard_gates[{index}]: SATISFIED requires evidence receipt"
                )
        elif receipt is not None:
            raise DataError(
                f"hard_gates[{index}]: UNSATISFIED evidence receipt must be null"
            )
    if len(gate_ids) != len(set(gate_ids)):
        raise DataError("ProgramControl.hard_gates: IDs must be unique")
    if not isinstance(control["reconciliation_receipt"], dict):
        raise DataError("ProgramControl.reconciliation_receipt: must be an object")
    _text(control["stop_condition"], "ProgramControl.stop_condition")
    _text(control["resume_condition"], "ProgramControl.resume_condition")
    if control["state"] in {"COMPLETE", "TERMINATED"} and (
        control["active_coordinates"] or control["authorized_queue"]
    ):
        raise DataError("terminal ProgramControl cannot dispatch work")
    if control["state"] == "COMPLETE" and any(
        gate["state"] != "SATISFIED" for gate in control["hard_gates"]
    ):
        raise DataError("complete ProgramControl cannot have an unsatisfied hard gate")
    if control["state"] == "ACTIVE" and (
        not control["reconciliation_receipt"] or not control["hard_gates"]
    ):
        raise DataError(
            "active ProgramControl needs a reconciliation receipt and hard gates"
        )
    if control["state"] == "TERMINATED":
        disposition = control["terminal_disposition"]
        if not isinstance(disposition, dict) or disposition.get("reason") not in {
            "OWNER_CANCELLED", "ABANDONED", "SUPERSEDED", "SAFETY",
        }:
            raise DataError("terminated ProgramControl needs a valid disposition")
    elif control["terminal_disposition"] is not None:
        raise DataError("terminal_disposition is only valid for TERMINATED")
    return control


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    digest_parser = subparsers.add_parser("policy-digest")
    digest_parser.add_argument("policy", type=Path)

    verify_parser = subparsers.add_parser("verify-policy")
    verify_parser.add_argument("policy", type=Path)
    verify_parser.add_argument("--authorities", type=Path, required=True)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--policy", type=Path, required=True)
    resolve_parser.add_argument("--authorities", type=Path, required=True)
    resolve_parser.add_argument("--task", type=Path, required=True)
    resolve_parser.add_argument("--model-flags", type=Path)

    program_parser = subparsers.add_parser("validate-program-control")
    program_parser.add_argument("control", type=Path)

    args = parser.parse_args()
    try:
        if args.command == "policy-digest":
            project_policy = read_json(args.policy.resolve())
            checked = validate_project_policy(
                project_policy, {}, require_accepted=False
            )
            print(checked["policy_sha256"])
        elif args.command == "verify-policy":
            result = validate_project_policy(
                read_json(args.policy.resolve()),
                read_json(args.authorities.resolve()),
            )
            print(json.dumps({
                "policy_id": result["policy_id"],
                "method_version": result["method_version"],
                "policy_sha256": result["policy_sha256"],
                "verified": True,
                "acceptance_receipt": result["acceptance_receipt"],
            }, indent=2))
        elif args.command == "resolve":
            flags = (
                read_json(args.model_flags.resolve())
                if args.model_flags is not None
                else None
            )
            permissions = resolve_permissions(
                read_json(args.policy.resolve()),
                read_json(args.authorities.resolve()),
                read_json(args.task.resolve()),
                flags,
            )
            print(json.dumps(permissions, indent=2))
        else:
            control = validate_program_control(read_json(args.control.resolve()))
            print(json.dumps({
                "program": control["program"],
                "state": control["state"],
                "schema_valid": True,
                "authority_verified": False,
            }, indent=2))
    except (DataError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
