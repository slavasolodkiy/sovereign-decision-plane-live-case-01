deterministic_verdict(accept_extraction).
verification(passport_number_format, pass).
verification(mrz_line_1_structure, pass).
verification(mrz_line_2_structure, pass).
verification(document_type_vs_mrz, pass).
verification(issuing_country_vs_mrz, pass).
verification(surname_vs_mrz, pass).
verification(given_names_vs_mrz, pass).
verification(document_number_check, pass).
verification(date_of_birth_check, pass).
verification(expiry_date_check, pass).
verification(optional_data_check, pass).
verification(composite_check, pass).
verification(passport_number_vs_mrz, pass).
verification(nationality_vs_mrz, pass).
verification(sex_vs_mrz, pass).
verification(date_of_birth_vs_mrz, pass).
verification(expiry_date_vs_mrz, pass).
verification(uncertainty_calibration, pass).
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
