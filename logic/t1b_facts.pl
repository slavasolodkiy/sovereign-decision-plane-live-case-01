deterministic_verdict(need_more_evidence).
verification(passport_number_format, pass).
verification(mrz_line_1_structure, fail).
verification(mrz_line_2_structure, pass).
verification(document_number_check, pass).
verification(date_of_birth_check, fail).
verification(expiry_date_check, fail).
verification(optional_data_check, fail).
verification(composite_check, fail).
verification(passport_number_vs_mrz, pass).
verification(nationality_vs_mrz, conflict).
verification(sex_vs_mrz, conflict).
verification(date_of_birth_vs_mrz, conflict).
verification(expiry_date_vs_mrz, conflict).
verification(uncertainty_calibration, fail).
no_declared_uncertainty.
observed(document_type, "P").
observed(issuing_country, "UTO").
observed(surname, "SAMPLE").
observed(given_names, "ALICE MARIA").
observed(nationality, "UTO").
observed(date_of_birth, "12 MAR 1990").
observed(sex, "F").
observed(expiry_date, "21 APR 2031").
observed(passport_number, "L898902C3").
