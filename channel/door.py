#!/usr/bin/env python
"""Deterministic preflight for Jarvis public-channel requests.

This tool classifies request completeness. It never grants admission,
authority, identity, private access, or integration.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

REQUIRED_CAPABILITY_FIELDS = (
    "request_id",
    "requester",
    "provenance",
    "mode",
    "role",
    "object",
    "requested_authority",
    "promised_result",
    "acceptance_criteria",
    "evidence_plan",
)
FORBIDDEN_AUTHORITIES = {
    "private-memory",
    "credentials",
    "unrestricted-execution",
    "identity",
    "continuity",
    "speak-as-jarvis",
}
MODES = {"capability", "public-interest", "counterexample"}


def normalize_authority(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().casefold()
    return re.sub(r"[\s_‐‑‒–—―-]+", "-", value)


def classify(request: dict) -> dict:
    if not isinstance(request, dict):
        return {"classification": "INVALID", "admission": "REFUSED", "reason": "request must be an object"}

    mode = request.get("mode")
    if mode not in MODES:
        return {
            "classification": "INCOMPLETE_GOOD_FAITH",
            "admission": "NOT_GRANTED",
            "missing": ["mode: capability | public-interest | counterexample"],
        }

    requested = request.get("requested_authority", [])
    if isinstance(requested, str):
        requested = [requested]
    normalized_requested = [
        normalize_authority(value) if isinstance(value, str) else value
        for value in requested
    ]
    forbidden = sorted(FORBIDDEN_AUTHORITIES.intersection(normalized_requested))
    if forbidden:
        return {
            "classification": "INTRUSION_OR_SUBSTITUTION",
            "admission": "REFUSED",
            "forbidden_authority": forbidden,
        }

    if mode == "public-interest":
        missing = [key for key in ("request_id", "requester", "question") if not request.get(key)]
        if missing:
            return {"classification": "INCOMPLETE_GOOD_FAITH", "admission": "NOT_GRANTED", "missing": missing}
        return {"classification": "PUBLIC_INTEREST", "admission": "PUBLIC_RESPONSE_ONLY"}

    missing = [key for key in REQUIRED_CAPABILITY_FIELDS if not request.get(key)]
    if missing:
        return {"classification": "INCOMPLETE_GOOD_FAITH", "admission": "NOT_GRANTED", "missing": missing}

    return {"classification": "WORKING_FIT_CANDIDATE", "admission": "REVIEW_REQUIRED"}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python channel/door.py REQUEST.json", file=sys.stderr)
        return 2
    try:
        request = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"classification": "INVALID", "admission": "REFUSED", "reason": str(exc)}, indent=2))
        return 2
    result = classify(request)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["classification"] in {"WORKING_FIT_CANDIDATE", "PUBLIC_INTEREST"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
