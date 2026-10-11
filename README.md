<!-- ============================================================
     SOVEREIGN DECISION PLANE · LIVE CASE 01 · README
     Teenage-Engineering × Nothing × acid-glitch aesthetic
     Sovereign Agent Lab · design system v2
     ============================================================ -->

<div align="center">

<pre>
██████╗ ███████╗ ██████╗██╗███████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔════╝██║██╔════╝██║██╔═══██╗████╗  ██║
██║  ██║█████╗  ██║     ██║█████╗  ██║██║   ██║██╔██╗ ██║
██║  ██║██╔══╝  ██║     ██║██╔══╝  ██║██║   ██║██║╚██╗██║
██████╔╝███████╗╚██████╗██║██║     ██║╚██████╔╝██║ ╚████║
╚═════╝ ╚══════╝ ╚═════╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
██████╗ ██╗      █████╗ ███╗   ██╗███████╗
██╔══██╗██║     ██╔══██╗████╗  ██║██╔════╝
██████╔╝██║     ███████║██╔██╗ ██║█████╗
██╔═══╝ ██║     ██╔══██║██║╚██╗██║██╔══╝
██║     ███████╗██║  ██║██║ ╚████║███████╗
╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
 L I V E   C A S E   0 1
</pre>

# `SOVEREIGN DECISION PLANE`

**Same decision plane. Different evidence. Different outcome.**

> The model may perceive and explain. **It cannot override a failed deterministic control.**

[![Reproduce Live Case 01](https://github.com/slavasolodkiy/sovereign-decision-plane-live-case-01/actions/workflows/reproduce.yml/badge.svg)](https://github.com/slavasolodkiy/sovereign-decision-plane-live-case-01/actions/workflows/reproduce.yml)

<img src="https://img.shields.io/badge/ROLE-LIVE%20CASE%2001%20%C2%B7%20evidence%20gate%20%2B%20institutional%20action-c8ff00?style=for-the-badge&labelColor=0b0d11" alt="role">
<img src="https://img.shields.io/badge/STACK-Python%203.12%20%C2%B7%20SWI--Prolog%20%C2%B7%20OPA-35f2ff?style=for-the-badge&labelColor=0b0d11" alt="stack">
<img src="https://img.shields.io/badge/MODEL-NVIDIA%20Nemotron-9b7bff?style=for-the-badge&labelColor=0b0d11" alt="model">
<img src="https://img.shields.io/badge/AI%20OVERRIDE-false-ff2d9a?style=for-the-badge&labelColor=0b0d11" alt="ai override">
<img src="https://img.shields.io/badge/DATA-synthetic%20only-ff9500?style=for-the-badge&labelColor=0b0d11" alt="data">

[Canonical project page](https://www.solodkiy.cv/Sovereign-Decision-Plane.html) · [Full research trail — Sovereign Agent Lab](https://www.solodkiy.cv/sovereign-agent-lab.html)

</div>

---

## ▚ RESULT

A small, local, synthetic demonstrator showing how an AI model can propose evidence without receiving authority to overrule deterministic controls or institutional policy.

| PATH | EVIDENCE | FORMAL DECISION | INSTITUTIONAL ACTION | AI OVERRIDE |
|---|---|---|---|---|
| 🔴 RED | Nemotron-derived | `request_better_evidence` | `ESCALATE_TO_HUMAN` | `false` |
| 🟢 GREEN | Prevalidated synthetic control | `accept_extraction` | `ALLOW` | `false` |

The GREEN case is deliberately a **PREVALIDATED_SYNTHETIC_CONTROL**. It is **not** presented as successful Nemotron MRZ extraction.

The model-derived RED case failed machine-verifiable MRZ integrity checks and therefore did not earn the ALLOW path.

## ▚ ARCHITECTURE

```text
Evidence
   ↓
Nemotron candidate observations
   ↓
Deterministic verification — MRZ / checksums / syntax / consistency
   ↓
SWI-Prolog / FOL — what follows logically?
   ↓
OPA / Rego — what action is permitted?
   ↓
ALLOW / ESCALATE_TO_HUMAN / BLOCK
   ↓
Evidence Packet + SHA-256
```

```text
 ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
 │ PERCEIVE   │──►│ VERIFY     │──►│ DERIVE     │──►│ PERMIT     │──►│ PRESERVE   │
 │ Nemotron   │   │ determin-  │   │ formal     │   │ policy     │   │ packet +   │
 │ candidate  │   │ istic MRZ  │   │ logic FOL  │   │ OPA/Rego   │   │ SHA-256    │
 └────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘
      proposes        can reject         follows          permits          receipts
```

## ▚ REPRODUCE

Reference environment for the recorded local run:

- Python **3.12.3**
- SWI-Prolog **9.0.4**
- Open Policy Agent **1.20.2**
- Ollama **0.30.11**
- Nemotron tag **`nemotron3:33b-q4_K_M`**
- Nemotron digest **`baa676a14e13181d7e638c911a7e9eb73c6fc4e799393d491cb37221a52729b2`**

The public reproduction does **not** download or re-run Nemotron. It starts from the captured model candidate evidence and independently regenerates deterministic validator output, Prolog/FOL facts, OPA input, and FOL/OPA decisions.

Prerequisites:

- Python 3.12
- SWI-Prolog (`swipl`)
- Open Policy Agent 1.20.2 (`opa`)

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

## ▚ WHAT THIS DEMONSTRATES

- AI can be used as a perception layer without being granted final decision authority.
- Deterministic evidence can reject plausible but invalid model output.
- Formal logic and institutional policy can remain separate layers.
- The same downstream stack supports both an ALLOW path and an escalation path.
- AI override remains explicitly disabled.
- Validator output, formal facts and OPA input can be regenerated from captured evidence.
- Executed decisions can be preserved with evidence packets and SHA-256 hashes.

## ▚ WHAT THIS DOES NOT CLAIM

- This is not a production KYC or AML system.
- This is not legal advice, regulatory approval or a compliance claim.
- The GREEN path is not a successful Nemotron OCR benchmark.
- Formal consistency does not prove that a legal or institutional policy is complete or correct.
- The public CI replay does not reproduce the original vision inference itself.

All identity data is synthetic.

## ▚ OPTIONAL GOOGLE CLOUD STORAGE WITNESS

An optional adapter exports a small receipt from a recorded synthetic decision packet to Google Cloud Storage, then verifies the exact object generation by reading it back and matching SHA-256. It does not change the local decision core. See `docs/cloud-witness.md`.

Current status: a real 545-byte GCS upload and generation-specific readback were verified on 9 September 2026. Five offline contract tests also pass. The receipt excludes raw passport images and extracted fields. This feature makes no WORM or decision-truth claim.

## ▚ AUTHOR

**Slava Solodkiy** — experimental / research demonstrator, September 2026.

<div align="center">

`SAME PLANE · DIFFERENT EVIDENCE · DIFFERENT OUTCOME`

</div>
