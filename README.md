# Sovereign Decision Plane — Live Case 01

> **Same decision plane. Different evidence. Different outcome.**

A small, local, synthetic demonstrator showing how an AI model can propose evidence without receiving authority to overrule deterministic controls or institutional policy.

## Result

| Path | Evidence | Formal decision | Institutional action | AI override |
|---|---|---|---|---|
| 🔴 RED | Nemotron-derived | `request_better_evidence` | `ESCALATE_TO_HUMAN` | `false` |
| 🟢 GREEN | Prevalidated synthetic control | `accept_extraction` | `ALLOW` | `false` |

The GREEN case is deliberately a **PREVALIDATED_SYNTHETIC_CONTROL**.

It is **not** presented as successful Nemotron MRZ extraction.

The model-derived RED case failed machine-verifiable MRZ integrity checks and therefore did not earn the ALLOW path.

## Architecture

```text
Evidence
   ↓
Nemotron
candidate observations
   ↓
Deterministic verification
MRZ / checksums / syntax / consistency
   ↓
SWI-Prolog / FOL
what follows logically?
   ↓
OPA / Rego
what action is permitted?
   ↓
ALLOW / ESCALATE_TO_HUMAN / BLOCK
   ↓
Evidence Packet + SHA-256
```

The model may perceive and explain.

**It cannot override a failed deterministic control.**

## Reproduce

Prerequisites:

- Python 3
- SWI-Prolog (`swipl`)
- Open Policy Agent (`opa`)

Run:

```bash
./run-demo.sh
```

Expected outcome:

```text
GREEN / PREVALIDATED CONTROL
DETERMINISTIC → ACCEPT_EXTRACTION
FOL           → accept_extraction
OPA           → ALLOW
AI OVERRIDE   → false

RED / MODEL-DERIVED
DETERMINISTIC → NEED_MORE_EVIDENCE
FOL           → request_better_evidence
OPA           → ESCALATE_TO_HUMAN
AI OVERRIDE   → false
```

The public demo replays the captured candidate evidence through the deterministic verifier, formal-logic layer and OPA policy.

It does **not** download or re-run Nemotron.

## What this demonstrates

- AI can be used as a perception layer without being granted final decision authority.
- Deterministic evidence can reject plausible but invalid model output.
- Formal logic and institutional policy can remain separate layers.
- The same downstream stack supports both an ALLOW path and an escalation path.
- AI override remains explicitly disabled.
- Executed decisions can be preserved with evidence packets and SHA-256 hashes.

## What this does not claim

- This is not a production KYC or AML system.
- This is not legal advice.
- This is not regulatory approval or a compliance claim.
- The GREEN path is not a successful Nemotron OCR benchmark.
- Formal consistency does not prove that a legal or institutional policy is complete or correct.

All identity data is synthetic.

## Sprint context

1. [FreeToken](https://www.solodkiy.cv/FreeToken.html)
2. [FOL-Lab / Qwen](https://www.solodkiy.cv/FOL-Qwen.html)
3. [Nemotron × FOL](https://www.dram.gold/Nemotron-FOL.html)
4. [AI Regulation Navigator](https://www.dram.gold/AI-Regulation.html)
5. [AI Regulation × FOL](https://www.solodkiy.cv/AI-Regulation-FOL.html)
6. [Algorithmic Sovereignty / Revolut](https://www.revolut.hot/revolut-FOL-sovereign.html)

Related preprint:

[Algorithmic Sovereignty in Digital Banking](https://figshare.com/articles/preprint/Algorithmic_Sovereignty_in_Digital_Banking/33427318)

Sprint wrap-up:

https://www.dram.gold/Sovereign-Decision-Plane.html

## Author

**Slava Solodkiy**

GitHub: https://github.com/slavasolodkiy

Experimental / research demonstrator, September 2026.
