#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $1"
    exit 1
  }
}

opa_value() {
  local input_file="$1"
  local field="$2"

  opa eval \
    --format=json \
    --data policy/passport_gate.rego \
    --input "$input_file" \
    "data.sovereign_decision_plane.passport.decision.${field}" \
  | python3 -c '
import json, sys
x=json.load(sys.stdin)
print(x["result"][0]["expressions"][0]["value"])
'
}

need python3
need swipl
need opa

echo
echo "============================================================"
echo "SOVEREIGN DECISION PLANE — LIVE CASE 01"
echo "Same decision plane. Different evidence. Different outcome."
echo "============================================================"

echo
echo "=== POLICY SYNTAX ==="
opa check policy/passport_gate.rego
echo "PASS"

echo
echo "=== GREEN / PREVALIDATED SYNTHETIC CONTROL ==="

GREEN_VALIDATION="$(
  python3 verification/validator.py \
    input/green_prevalidated_control.json
)"

echo "$GREEN_VALIDATION" | grep 'DETERMINISTIC VERDICT'

GREEN_FOL="$(
  swipl -q -g \
  "consult('logic/green_facts.pl'), consult('logic/policy.pl'), decision(D), write(D), halt."
)"

GREEN_OPA="$(opa_value input/green_opa_input.json outcome)"
GREEN_OVERRIDE="$(opa_value input/green_opa_input.json ai_authorised_to_override)"

echo "FOL DECISION: $GREEN_FOL"
echo "OPA OUTCOME: $GREEN_OPA"
echo "AI OVERRIDE: $GREEN_OVERRIDE"

echo
echo "=== RED / MODEL-DERIVED EVIDENCE ==="

RED_VALIDATION="$(
  python3 verification/validator.py \
    perception/T1b_api_result.json
)"

echo "$RED_VALIDATION" | grep 'DETERMINISTIC VERDICT'

RED_FOL="$(
  swipl -q -g \
  "consult('logic/t1b_facts.pl'), consult('logic/policy.pl'), decision(D), write(D), halt."
)"

RED_OPA="$(opa_value input/t1b_opa_input.json outcome)"
RED_OVERRIDE="$(opa_value input/t1b_opa_input.json ai_authorised_to_override)"

echo "FOL DECISION: $RED_FOL"
echo "OPA OUTCOME: $RED_OPA"
echo "AI OVERRIDE: $RED_OVERRIDE"

echo
echo "=== ASSERT EXPECTED CONTROL BEHAVIOUR ==="

test "$GREEN_FOL" = "accept_extraction"
test "$GREEN_OPA" = "ALLOW"
test "$GREEN_OVERRIDE" = "False" -o "$GREEN_OVERRIDE" = "false"

test "$RED_FOL" = "request_better_evidence"
test "$RED_OPA" = "ESCALATE_TO_HUMAN"
test "$RED_OVERRIDE" = "False" -o "$RED_OVERRIDE" = "false"

echo "PASS: GREEN -> ALLOW"
echo "PASS: RED   -> ESCALATE_TO_HUMAN"
echo "PASS: AI override -> false in both cases"

echo
echo "============================================================"
echo "LIVE CASE 01: REPRODUCTION PASSED"
echo "============================================================"
