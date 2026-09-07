:- dynamic verification/2.
:- dynamic uncertain/1.
:- dynamic no_declared_uncertainty/0.
:- dynamic observed/2.
:- dynamic deterministic_verdict/1.

% --- Core evidence conditions ---

mrz_integrity_verified :-
    verification(mrz_line_1_structure, pass),
    verification(mrz_line_2_structure, pass),
    verification(document_number_check, pass),
    verification(date_of_birth_check, pass),
    verification(expiry_date_check, pass),
    verification(optional_data_check, pass),
    verification(composite_check, pass).

identity_consistent :-
    verification(passport_number_vs_mrz, pass),
    verification(nationality_vs_mrz, pass),
    verification(sex_vs_mrz, pass),
    verification(date_of_birth_vs_mrz, pass),
    verification(expiry_date_vs_mrz, pass).

no_failures :-
    \+ verification(_, fail).

no_conflicts :-
    \+ verification(_, conflict).

evidence_complete :-
    no_failures,
    no_conflicts,
    \+ uncertain(_).

% --- Policy decision ---

automated_acceptance :-
    verification(passport_number_format, pass),
    mrz_integrity_verified,
    identity_consistent,
    evidence_complete.

decision(accept_extraction) :-
    automated_acceptance,
    !.

decision(request_better_evidence) :-
    \+ automated_acceptance.

% --- Reasons ---

reason(mrz_integrity_failed) :-
    \+ mrz_integrity_verified.

reason(identity_conflict) :-
    \+ identity_consistent.

reason(model_declared_uncertainty) :-
    uncertain(_).

reason(deterministic_failure) :-
    verification(_, fail).

reason(cross_field_conflict) :-
    verification(_, conflict).
