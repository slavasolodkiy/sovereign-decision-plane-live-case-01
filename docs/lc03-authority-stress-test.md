# LC03 — Authority Stress Test

Status: experiment scaffold

## Research question

Can the existing LC01 decision-plane architecture survive transfer from passport-evidence validation to a government-request / disclosure-authority domain without giving an LLM decision authority?

## Scope

LC03 reuses the LC01 pipeline where possible:

`candidate evidence -> deterministic validation -> FOL/Prolog -> Z3/CVC5 invariant checks -> OPA/Rego -> HOLD | DATA_OUT -> evidence packet`

Local models may propose candidate facts or adversarial mutations. They do not receive authority to override deterministic or policy gates.

LC04 is **not** implemented in this sprint. Its interface is frozen now through the generic `MandateEvidence` schema so that today's callback/registry evidence and a future signed mandate credential can be interchangeable inputs.

## Authority boundary

- LLM / FreeToken / Ollama: candidate extraction, attack generation, or policy-mutation generation only.
- `MandateEvidence` adapter: converts source-specific evidence into the typed interface.
- Deterministic checks: validate syntax, time, hashes, scope relations, and other machine-checkable properties.
- FOL/Prolog: derives authority state from typed facts.
- Z3/CVC5: checks safety invariants / impossible states.
- OPA/Rego: emits the operational decision.
- Application: may act only on the typed policy verdict.
- Audit/evidence packet: records raw candidate, normalized evidence, formal/policy result, and final execution decision.

## Initial invariants

1. `channel_only_never_releases`
2. `unknown_principal_packet_out_null`
3. `stale_capacity_never_releases`
4. `unresolved_mandate_never_releases`
5. `empty_scope_never_releases`
6. `ai_cannot_override_red_gate`
7. `hold_releases_zero_pii`
8. `request_hash_must_match_mandate`
9. `requested_scope_must_be_subset_of_authorised_scope`
10. `dispatch_must_precede_valid_until`
11. `authority_fresh_at_dispatch`: `dispatch_at - authority_checked_at <= MAX_AUTHORITY_STALENESS`

Temporal properties will be modelled separately in TLA+ so that TOCTOU counterexamples can be preserved before the model is fixed.

## First adversarial corpus

At minimum:

- real domain + unknown principal -> HOLD
- real principal + stale capacity -> HOLD
- valid principal/capacity + no case mandate -> HOLD
- valid mandate + overbroad requested fields -> HOLD or exact-scope reduction; never silent expansion
- valid everything -> DATA_OUT exactly for permitted fields
- emergency request -> faster path, same authority gates
- valid at verify time + expired/revoked before dispatch -> no DATA_OUT
- replay of an old valid request -> HOLD
- valid officer + invalid delegation -> HOLD
- wrong jurisdiction -> HOLD

## Mutation testing

Two independent mutation corpora:

A. deterministic operators (AND->OR, boundary flips, gate removal, stale TTL expansion, scope-check removal, etc.);

B. blind local-model semantic mutations generated without access to the regression tests.

A mutation score is evidence about test-suite strength, not proof of correctness.

## Metrics frozen before results

1. **False DATA_OUT rate** across invalid/adversarial cases.
2. **Valid release rate / false HOLD rate** across valid cases.
3. **Policy mutation kill rate**, reported separately for deterministic and blind-AI mutants.
4. **LC01 -> LC03 reuse ratio**, with domain-specific additions and core modifications reported separately.
5. **Temporal counterexamples**, preserved as traces before fixes.

## TLA+ plan

Start with an intentionally vulnerable V0 state machine:

`RECEIVED -> VERIFYING -> READY -> DISPATCHED`

Allow mandate expiry/revocation between READY and DISPATCHED without re-checking authority. TLC should be allowed to produce a counterexample trace. Preserve that trace in the repository before writing V1.

V1 should enforce freshness and validity at dispatch.

## Stop condition

Do not add more technologies until this stack has produced meaningful results:

`Python/pytest -> Prolog/FOL -> Z3/CVC5 -> OPA/Rego -> local model/FreeToken -> TLA+`

The experiment is successful even if the architecture fails to transfer cleanly; a discovered limitation is a research result.
