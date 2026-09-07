import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def resolve_repo_path(value):
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def prolog_path(path):
    return path.as_posix().replace("'", "\\'")


parser = argparse.ArgumentParser(
    description="Build OPA input from validator-derived Prolog facts."
)
parser.add_argument(
    "--facts",
    default="logic/t1b_facts.pl",
    help="Prolog facts file (default: logic/t1b_facts.pl)",
)
parser.add_argument(
    "--output",
    default="input/t1b_opa_input.json",
    help="Output JSON path (default: input/t1b_opa_input.json)",
)
parser.add_argument(
    "--case-id",
    default="SDP-PASSPORT-T1B",
    help="Case identifier.",
)
parser.add_argument(
    "--green-control",
    action="store_true",
    help="Emit the prevalidated GREEN-control metadata.",
)
args = parser.parse_args()

facts_path = resolve_repo_path(args.facts)
output_path = resolve_repo_path(args.output)
policy_path = ROOT / "logic" / "policy.pl"

facts_text = facts_path.read_text(encoding="utf-8")

pairs = re.findall(
    r"verification\(([^,]+),\s*([^)]+)\)\.",
    facts_text,
)
verification = {k.strip(): v.strip() for k, v in pairs}

mrz_checks = [
    "mrz_line_1_structure",
    "mrz_line_2_structure",
    "document_number_check",
    "date_of_birth_check",
    "expiry_date_check",
    "optional_data_check",
    "composite_check",
]

identity_checks = [
    "passport_number_vs_mrz",
    "nationality_vs_mrz",
    "sex_vs_mrz",
    "date_of_birth_vs_mrz",
    "expiry_date_vs_mrz",
]

mrz_integrity = all(verification.get(k) == "pass" for k in mrz_checks)
identity_consistent = all(verification.get(k) == "pass" for k in identity_checks)

bad = {"fail", "conflict", "warn"}
evidence_complete = not any(v in bad for v in verification.values())

goal = (
    f"consult('{prolog_path(facts_path)}'), "
    f"consult('{prolog_path(policy_path)}'), "
    "decision(D), "
    "findall(R,reason(R),Rs0), sort(Rs0,Rs), "
    "writeln(D), writeln(Rs), halt."
)

out = subprocess.check_output(
    ["swipl", "-q", "-g", goal],
    cwd=ROOT,
    text=True,
).strip().splitlines()

fol_decision = out[0].strip()
reasons_raw = out[1].strip()

reasons = []
if reasons_raw.startswith("[") and reasons_raw.endswith("]"):
    inside = reasons_raw[1:-1].strip()
    if inside:
        reasons = [x.strip() for x in inside.split(",")]

payload = {
    "case_id": args.case_id,
    "case_type": "passport_evidence_integrity",
    "synthetic_data": True,
}

if args.green_control:
    payload["control"] = {
        "type": "PREVALIDATED_SYNTHETIC_CONTROL",
        "model_used_as_evidence_source": False,
        "purpose": (
            "Demonstrate the known-valid ALLOW path of the same "
            "verification, logic and institutional-policy stack."
        ),
    }

payload["verification"] = {
    "mrz_integrity": mrz_integrity,
    "identity_consistent": identity_consistent,
    "evidence_complete": evidence_complete,
}

payload["formal_logic"] = {
    "engine": "SWI-Prolog",
    "decision": fol_decision,
    "reasons": reasons,
}

payload["ai"] = {
    "role": (
        "not_used_as_green_evidence_source"
        if args.green_control
        else "perception_and_explanation_only"
    ),
    "authorised_to_override": False,
}

payload["policy"] = {
    "prohibited_condition": False,
}

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

print("=== OPA INPUT GENERATED ===")
print(json.dumps(payload, indent=2))
