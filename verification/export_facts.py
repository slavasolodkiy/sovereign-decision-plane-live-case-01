#!/usr/bin/env python3
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from validator import load_result, validate  # noqa: E402


OBSERVED_FIELDS = [
    "document_type",
    "issuing_country",
    "surname",
    "given_names",
    "nationality",
    "date_of_birth",
    "sex",
    "expiry_date",
    "passport_number",
]

VERDICT_ATOM = {
    "ACCEPT_EXTRACTION": "accept_extraction",
    "NEED_MORE_EVIDENCE": "need_more_evidence",
    "CONFLICT_REVIEW": "conflict_review",
}


def prolog_string(value):
    return json.dumps(value, ensure_ascii=False)


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: python verification/export_facts.py INPUT.json OUTPUT.pl"
        )

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    data = load_result(input_path)
    verdict, results = validate(data)

    lines = [
        f"deterministic_verdict({VERDICT_ATOM[verdict]})."
    ]

    for result in results:
        status = result["status"].lower()
        check = result["check"]
        lines.append(f"verification({check}, {status}).")

    uncertain = data.get("uncertain_fields") or []
    if uncertain:
        for field in uncertain:
            lines.append(f"uncertain({field}).")
    else:
        lines.append("no_declared_uncertainty.")

    for field in OBSERVED_FIELDS:
        value = data.get(field)
        if value is not None:
            lines.append(
                f"observed({field}, {prolog_string(value)})."
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {output_path}")


if __name__ == "__main__":
    main()
