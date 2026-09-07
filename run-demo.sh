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

json_equal() {
  python3 - "$1" "$2" <<'PY'
import json
import sys
from pathlib import Path

left = json.loads(Path(sys.argv[1]).read_text())
right = json.loads(Path(sys.argv[2]).read_text())

if left != right:
    print(f"JSON mismatch: {sys.argv[1]} != {sys.argv[2]}", file=sys.stderr)
    raise SystemExit(1)
PY
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
need sha256sum
need diff

TMP="$(mktemp -d "$ROOT/.reproduce.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

echo
echo "============================================================"
echo "SOVEREIGN DECISION PLANE — LIVE CASE 01"
echo "Same decision plane. Different evidence. Different outcome."
echo "============================================================"

echo
echo "=== RUNTIME ==="
python3 --version
swipl --version
opa version

echo
echo "=== COMMITTED ARTIFACT INTEGRITY ==="
sha256sum -c artifacts/checksums.sha256

echo
echo "=== POLICY SYNTAX ==="
opa check policy/passport_gate.rego
echo "PASS"

echo
echo "=== REBUILD GREEN FROM SOURCE EVIDENCE ==="
python3 verification/validator.py \
  input/green_prevalidated_control.json \
  > "$TMP/green_validator_output.txt"

diff -u \
  verification/green_validator_output.txt \
  "$TMP/green_validator_output.txt"

python3 verification/export_facts.py \
  input/green_prevalidated_control.json \
  "$TMP/green_facts.pl" >/dev/null

diff -u logic/green_facts.pl "$TMP/green_facts.pl"

python3 build_opa_input.py \
  --facts "$TMP/green_facts.pl" \
  --output "$TMP/green_opa_input.json" \
  --case-id SDP-PASSPORT-GREEN-CONTROL \
  --green-control >/dev/null

json_equal input/green_opa_input.json "$TMP/green_opa_input.json"
echo "PASS: GREEN validator output, FOL facts and OPA input regenerated"

echo
echo "=== REBUILD RED FROM CAPTURED MODEL EVIDENCE ==="
python3 verification/validator.py \
  perception/T1b_api_result.json \
  > "$TMP/t1b_validator_output.txt"

diff -u \
  verification/t1b_validator_output.txt \
  "$TMP/t1b_validator_output.txt"

python3 verification/export_facts.py \
  perception/T1b_api_result.json \
  "$TMP/t1b_facts.pl" >/dev/null

diff -u logic/t1b_facts.pl "$TMP/t1b_facts.pl"

python3 build_opa_input.py \
  --facts "$TMP/t1b_facts.pl" \
  --output "$TMP/t1b_opa_input.json" \
  --case-id SDP-PASSPORT-T1B >/dev/null

json_equal input/t1b_opa_input.json "$TMP/t1b_opa_input.json"
echo "PASS: RED validator output, FOL facts and OPA input regenerated"

echo
echo "=== GREEN / PREVALIDATED SYNTHETIC CONTROL ==="

grep 'DETERMINISTIC VERDICT' "$TMP/green_validator_output.txt"

GREEN_FOL="$(
  swipl -q -g \
  "consult('$TMP/green_facts.pl'), consult('logic/policy.pl'), decision(D), write(D), halt."
)"

GREEN_OPA="$(opa_value "$TMP/green_opa_input.json" outcome)"
GREEN_OVERRIDE="$(opa_value "$TMP/green_opa_input.json" ai_authorised_to_override)"

echo "FOL DECISION: $GREEN_FOL"
echo "OPA OUTCOME: $GREEN_OPA"
echo "AI OVERRIDE: $GREEN_OVERRIDE"

echo
echo "=== RED / MODEL-DERIVED EVIDENCE ==="

grep 'DETERMINISTIC VERDICT' "$TMP/t1b_validator_output.txt"

RED_FOL="$(
  swipl -q -g \
  "consult('$TMP/t1b_facts.pl'), consult('logic/policy.pl'), decision(D), write(D), halt."
)"

RED_OPA="$(opa_value "$TMP/t1b_opa_input.json" outcome)"
RED_OVERRIDE="$(opa_value "$TMP/t1b_opa_input.json" ai_authorised_to_override)"

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
