import json
import re
import subprocess
from pathlib import Path

SRC = Path("/root/nemotron-pilot")
facts_text = (SRC / "t1b_facts.pl").read_text()

pairs = re.findall(
    r'verification\(([^,]+),\s*([^)]+)\)\.',
    facts_text
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

bad = {"fail", "conflict"}
evidence_complete = not any(v in bad for v in verification.values())

goal = (
    "consult('t1b_facts.pl'), consult('policy.pl'), "
    "decision(D), "
    "findall(R,reason(R),Rs0), sort(Rs0,Rs), "
    "writeln(D), writeln(Rs), halt."
)

out = subprocess.check_output(
    ["swipl", "-q", "-g", goal],
    cwd=SRC,
    text=True
).strip().splitlines()

fol_decision = out[0].strip()
reasons_raw = out[1].strip()

reasons = []
if reasons_raw.startswith("[") and reasons_raw.endswith("]"):
    inside = reasons_raw[1:-1].strip()
    if inside:
        reasons = [x.strip() for x in inside.split(",")]

payload = {
    "case_id": "SDP-PASSPORT-T1B",
    "case_type": "passport_evidence_integrity",
    "synthetic_data": True,

    "verification": {
        "mrz_integrity": mrz_integrity,
        "identity_consistent": identity_consistent,
        "evidence_complete": evidence_complete
    },

    "formal_logic": {
        "engine": "SWI-Prolog",
        "decision": fol_decision,
        "reasons": reasons
    },

    "ai": {
        "role": "perception_and_explanation_only",
        "authorised_to_override": False
    },

    "policy": {
        "prohibited_condition": False
    }
}

Path("input/t1b_opa_input.json").write_text(
    json.dumps(payload, indent=2) + "\n"
)

print("=== OPA INPUT GENERATED ===")
print(json.dumps(payload, indent=2))
