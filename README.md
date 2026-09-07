# Sovereign Decision Plane — Live Case 01

[![Reproduce Live Case 01](https://github.com/slavasolodkiy/sovereign-decision-plane-live-case-01/actions/workflows/reproduce.yml/badge.svg)](https://github.com/slavasolodkiy/sovereign-decision-plane-live-case-01/actions/workflows/reproduce.yml)

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

Reference environment for the recorded local run:

- Python **3.12.3**
- SWI-Prolog **9.0.4**
- Open Policy Agent **1.20.2**
- Ollama **0.30.11**
- Nemotron tag **`nemotron3:33b-q4_K_M`**
- Nemotron digest **`baa676a14e13181d7e638c911a7e9eb73c6fc4e799393d491cb37221a52729b2`**

The public reproduction does **not** download or re-run Nemotron. It starts from
the captured model candidate evidence and independently regenerates:

1. deterministic validator output;
2. Prolog/FOL facts;
3. OPA input;
4. FOL and OPA decisions.

Each regenerated intermediate is checked against the committed artifact before
the expected GREEN/RED outcomes are asserted.

Prerequisites:

- Python 3.12
- SWI-Prolog (`swipl`)
- Open Policy Agent 1.20.2 (`opa`)

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

GitHub Actions runs the same reproduction on a public GitHub-hosted Ubuntu
runner. The workflow pins Python 3.12 and OPA 1.20.2; the installed SWI-Prolog
version is printed in the job log.

## What this demonstrates

- AI can be used as a perception layer without being granted final decision authority.
- Deterministic evidence can reject plausible but invalid model output.
- Formal logic and institutional policy can remain separate layers.
- The same downstream stack supports both an ALLOW path and an escalation path.
- AI override remains explicitly disabled.
- Validator output, formal facts and OPA input can be regenerated from the captured evidence.
- Executed decisions can be preserved with evidence packets and SHA-256 hashes.

## What this does not claim

- This is not a production KYC or AML system.
- This is not legal advice.
- This is not regulatory approval or a compliance claim.
- The GREEN path is not a successful Nemotron OCR benchmark.
- Formal consistency does not prove that a legal or institutional policy is complete or correct.
- The public CI replay does not reproduce the original vision inference itself.

All identity data is synthetic.

## Public artifacts

- [Sprint wrap-up — Sovereign Decision Plane](https://www.dram.gold/Sovereign-Decision-Plane.html)
- [Nemotron × FOL experiment page](https://www.dram.gold/Nemotron-FOL.html)
- [X / @NansenID](https://x.com/NansenID/status/2096900477204001043)
- [X / @SolodkiyUK](https://x.com/SolodkiyUK/status/2096918298596098323)

## Sprint context

1. [FreeToken](https://www.solodkiy.cv/FreeToken.html)
2. [FOL-Lab / Qwen](https://www.solodkiy.cv/FOL-Qwen.html)
3. [Nemotron × FOL](https://www.dram.gold/Nemotron-FOL.html)
4. [AI Regulation Navigator](https://www.dram.gold/AI-Regulation.html)
5. [AI Regulation × FOL](https://www.solodkiy.cv/AI-Regulation-FOL.html)
6. [Algorithmic Sovereignty / Revolut](https://www.revolut.hot/revolut-FOL-sovereign.html)

Related preprint:

[Algorithmic Sovereignty in Digital Banking](https://figshare.com/articles/preprint/Algorithmic_Sovereignty_in_Digital_Banking/33427318)

## Author

**Slava Solodkiy**

GitHub: https://github.com/slavasolodkiy

Experimental / research demonstrator, September 2026.
