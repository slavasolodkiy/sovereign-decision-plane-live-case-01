# Input cases

This repository contains two deliberately different evidence paths through the
same downstream decision plane.

- `t1b_opa_input.json` is derived from the captured Nemotron candidate
  extraction in `perception/T1b_api_result.json`. Its machine-readable MRZ
  evidence fails deterministic checks and therefore escalates.
- `green_prevalidated_control.json` is a **PREVALIDATED SYNTHETIC CONTROL**.
  It is intentionally known-good input used to prove that the same
  verification → Prolog/FOL → OPA/Rego stack has a valid `ALLOW` path.

The GREEN case is **not** a successful Nemotron OCR result and should not be
described as one. Its purpose is positive-control testing of the downstream
decision plane.
