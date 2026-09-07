import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CONTROL_JSON = ROOT / "input/green_prevalidated_control.json"
FACTS = ROOT / "logic/green_facts.pl"
PROLOG_POLICY = ROOT / "logic/policy.pl"
REGO_POLICY = ROOT / "policy/passport_gate.rego"

CASE_ID = "SDP-PASSPORT-GREEN-CONTROL"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------
# Read actual deterministic verification facts
# ---------------------------------------------------------

facts_text = FACTS.read_text()

pairs = re.findall(
    r'verification\(([^,]+),\s*([^)]+)\)\.',
    facts_text
)

verification = {
    k.strip(): v.strip()
    for k, v in pairs
}

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

mrz_integrity = all(
    verification.get(k) == "pass"
    for k in mrz_checks
)

identity_consistent = all(
    verification.get(k) == "pass"
    for k in identity_checks
)

evidence_complete = not any(
    value in {"fail", "conflict"}
    for value in verification.values()
)


# ---------------------------------------------------------
# Execute actual Prolog/FOL decision
# ---------------------------------------------------------

goal = (
    "consult('logic/green_facts.pl'), "
    "consult('logic/policy.pl'), "
    "decision(D), "
    "findall(R,reason(R),Rs0), sort(Rs0,Rs), "
    "writeln(D), writeln(Rs), halt."
)

out = subprocess.check_output(
    ["swipl", "-q", "-g", goal],
    cwd=ROOT,
    text=True
).strip().splitlines()

fol_decision = out[0].strip()

reasons_raw = out[1].strip()
fol_reasons = []

if reasons_raw.startswith("[") and reasons_raw.endswith("]"):
    body = reasons_raw[1:-1].strip()
    if body:
        fol_reasons = [x.strip() for x in body.split(",")]


# ---------------------------------------------------------
# Build OPA input
# ---------------------------------------------------------

opa_input = {
    "case_id": CASE_ID,
    "case_type": "passport_evidence_integrity",
    "synthetic_data": True,

    "control": {
        "type": "PREVALIDATED_SYNTHETIC_CONTROL",
        "model_used_as_evidence_source": False,
        "purpose": (
            "Demonstrate the known-valid ALLOW path of the "
            "same verification, logic and institutional-policy stack."
        )
    },

    "verification": {
        "mrz_integrity": mrz_integrity,
        "identity_consistent": identity_consistent,
        "evidence_complete": evidence_complete
    },

    "formal_logic": {
        "engine": "SWI-Prolog",
        "decision": fol_decision,
        "reasons": fol_reasons
    },

    "ai": {
        "role": "not_used_as_green_evidence_source",
        "authorised_to_override": False
    },

    "policy": {
        "prohibited_condition": False
    }
}

opa_input_path = ROOT / "input/green_opa_input.json"

opa_input_path.write_text(
    json.dumps(opa_input, indent=2) + "\n"
)


# ---------------------------------------------------------
# Execute actual OPA institutional decision
# ---------------------------------------------------------

raw = subprocess.check_output(
    [
        "opa", "eval",
        "--format=json",
        "--data", str(REGO_POLICY),
        "--input", str(opa_input_path),
        "data.sovereign_decision_plane.passport.decision"
    ],
    text=True
)

envelope = json.loads(raw)

decision = envelope["result"][0]["expressions"][0]["value"]

decision_path = (
    ROOT /
    "evidence/SDP-PASSPORT-GREEN-CONTROL-opa-decision.json"
)

decision_path.write_text(
    json.dumps(decision, indent=2) + "\n"
)


# ---------------------------------------------------------
# Evidence packet
# ---------------------------------------------------------

artifacts = {}

for rel in [
    "input/green_prevalidated_control.json",
    "verification/green_validator_output.txt",
    "logic/green_facts.pl",
    "logic/policy.pl",
    "input/green_opa_input.json",
    "policy/passport_gate.rego",
    "evidence/SDP-PASSPORT-GREEN-CONTROL-opa-decision.json",
]:
    path = ROOT / rel
    artifacts[rel] = {
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size
    }


packet = {
    "artifact_type": "sovereign_decision_plane_evidence_packet",
    "artifact_version": "0.1.0",

    "generated_at_utc": datetime.now(timezone.utc).isoformat(),

    "case": {
        "case_id": CASE_ID,
        "case_type": "passport_evidence_integrity",
        "synthetic_data": True,
        "environment": "local_olares_demonstrator"
    },

    "control_design": {
        "type": "PREVALIDATED_SYNTHETIC_CONTROL",
        "nemotron_perception_test": False,
        "purpose": (
            "Positive control proving that valid evidence can "
            "traverse the same downstream stack to ALLOW."
        )
    },

    "verification": opa_input["verification"],

    "formal_logic": opa_input["formal_logic"],

    "operational_decision": decision,

    "authority_boundary": {
        "ai_authorised_to_override": False,
        "decision_authority": "deterministic verification + formal logic + OPA policy"
    },

    "artifacts": artifacts,

    "integrity_note": (
        "This GREEN case is deliberately a prevalidated synthetic "
        "control and is NOT presented as successful Nemotron MRZ "
        "extraction. Its purpose is to prove the positive ALLOW path "
        "of the deterministic and policy stack. The separate RED case "
        "contains model-derived evidence and results in escalation."
    )
}

packet_path = (
    ROOT /
    "evidence/SDP-PASSPORT-GREEN-CONTROL-evidence.json"
)

packet_path.write_text(
    json.dumps(packet, indent=2) + "\n"
)


print()
print("============================================================")
print("SOVEREIGN DECISION PLANE — GREEN CONTROL")
print("============================================================")
print("CASE:", CASE_ID)
print("CONTROL: PREVALIDATED_SYNTHETIC_CONTROL")
print("MRZ INTEGRITY:", mrz_integrity)
print("IDENTITY CONSISTENT:", identity_consistent)
print("FOL:", fol_decision)
print("OPA:", decision["outcome"])
print("AI OVERRIDE:", decision["ai_authorised_to_override"])
print()
print("EVIDENCE PACKET:")
print(packet_path)
print()
print("SHA256:")
print(sha256_file(packet_path))
print("============================================================")
