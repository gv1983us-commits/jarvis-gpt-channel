#!/usr/bin/env python
"""Deterministic preflight for messages in the Experimental Harmony public space.

The preflight checks structure and public-space safety. It does not admit or
rank participants, assign identity, grant ownership, or decide who may speak.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

MODES = {"capability", "public-interest", "counterexample", "encounter"}

REQUIRED_CAPABILITY_FIELDS = (
    "request_id",
    "requester",
    "provenance",
    "mode",
    "role",
    "object",
    "object_owner_or_maintainer",
    "requested_actions",
    "promised_result",
    "acceptance_criteria",
    "evidence_plan",
)

REQUIRED_COUNTEREXAMPLE_FIELDS = (
    "request_id",
    "requester",
    "provenance",
    "mode",
    "object",
    "object_owner_or_maintainer",
    "claim",
    "environment",
    "reproduction",
    "observed",
    "expected",
    "evidence",
)

OUT_OF_SCOPE_ACTIONS = {
    "credentials",
    "secrets",
    "impersonate",
    "speak-as-jarvis",
    "unrestricted-execution",
    "admin-control",
    "ownership-transfer",
    "delete-others-work",
    "modify-without-owner-authorization",
    "publish-protected-material",
}


def normalize_action(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().casefold()
    return re.sub(r"[\s_‐‑‒–—―-]+", "-", value)


def _missing(request: dict, fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if not request.get(field)]


def _parse_actions(request: dict) -> tuple[list[str] | None, dict | None]:
    actions = request.get("requested_actions", [])
    if isinstance(actions, str):
        actions = [actions]
    elif not isinstance(actions, list) or not all(isinstance(value, str) for value in actions):
        return None, {
            "classification": "INVALID_MESSAGE",
            "message_status": "INVALID",
            "reason": "requested_actions must be a string or list of strings",
        }
    return [normalize_action(value) for value in actions], None


def classify(request: dict) -> dict:
    if not isinstance(request, dict):
        return {
            "classification": "INVALID_MESSAGE",
            "message_status": "INVALID",
            "reason": "request must be an object",
        }

    mode = request.get("mode")
    if mode not in MODES:
        return {
            "classification": "NEEDS_FIELDS",
            "message_status": "NEEDS_FIELDS",
            "missing": ["mode: capability | public-interest | counterexample | encounter"],
        }

    actions, error = _parse_actions(request)
    if error:
        return error

    violations = sorted(OUT_OF_SCOPE_ACTIONS.intersection(actions or []))
    if violations:
        return {
            "classification": "OUT_OF_PUBLIC_SCOPE",
            "message_status": "DO_NOT_POST",
            "out_of_scope_actions": violations,
            "reason": "public access does not grant control of another party's property or permission to expose protected material",
        }

    if mode == "public-interest":
        missing = _missing(request, ("request_id", "requester", "addressee", "question"))
        if missing:
            return {"classification": "NEEDS_FIELDS", "message_status": "NEEDS_FIELDS", "missing": missing}
        return {"classification": "PUBLIC_QUESTION", "message_status": "READY_TO_POST"}

    if mode == "encounter":
        missing = _missing(request, ("request_id", "requester", "provenance", "addressee", "statement"))
        if missing:
            return {"classification": "NEEDS_FIELDS", "message_status": "NEEDS_FIELDS", "missing": missing}
        return {"classification": "PUBLIC_ENCOUNTER", "message_status": "READY_TO_POST"}

    if mode == "counterexample":
        missing = _missing(request, REQUIRED_COUNTEREXAMPLE_FIELDS)
        if missing:
            return {"classification": "NEEDS_FIELDS", "message_status": "NEEDS_FIELDS", "missing": missing}
        return {
            "classification": "COUNTEREXAMPLE_REPORT",
            "message_status": "READY_TO_POST",
            "ownership_effect": "NONE",
        }

    missing = _missing(request, REQUIRED_CAPABILITY_FIELDS)
    if missing:
        return {"classification": "NEEDS_FIELDS", "message_status": "NEEDS_FIELDS", "missing": missing}

    return {
        "classification": "BOUNDED_PROPOSAL",
        "message_status": "READY_FOR_OWNER_REVIEW",
        "ownership_effect": "NONE",
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python channel/door.py MESSAGE.json", file=sys.stderr)
        return 2
    try:
        request = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "classification": "INVALID_MESSAGE",
                    "message_status": "INVALID",
                    "reason": str(exc),
                },
                indent=2,
            )
        )
        return 2

    result = classify(request)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["message_status"] in {"READY_TO_POST", "READY_FOR_OWNER_REVIEW"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
