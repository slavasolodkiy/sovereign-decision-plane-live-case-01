package sovereign_decision_plane.passport

default decision := {
    "outcome": "ESCALATE_TO_HUMAN",
    "policy_conditions_satisfied": false,
    "reasons": ["No explicit allow condition was satisfied."],
    "ai_authorised_to_override": false
}

decision := {
    "outcome": "BLOCK",
    "policy_conditions_satisfied": false,
    "reasons": ["A prohibited institutional condition is present."],
    "ai_authorised_to_override": false
} if {
    input.policy.prohibited_condition == true
}

decision := {
    "outcome": "ESCALATE_TO_HUMAN",
    "policy_conditions_satisfied": false,
    "reasons": input.formal_logic.reasons,
    "ai_authorised_to_override": false
} if {
    input.policy.prohibited_condition == false
    input.formal_logic.decision == "request_better_evidence"
}

decision := {
    "outcome": "ALLOW",
    "policy_conditions_satisfied": true,
    "reasons": ["Evidence integrity and formal decision requirements passed."],
    "ai_authorised_to_override": false
} if {
    input.policy.prohibited_condition == false
    input.formal_logic.decision == "accept_extraction"
    input.verification.mrz_integrity == true
    input.verification.identity_consistent == true
    input.verification.evidence_complete == true
}
