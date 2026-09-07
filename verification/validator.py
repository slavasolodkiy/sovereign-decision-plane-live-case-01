import json
import re
import sys
from datetime import datetime
from pathlib import Path

WEIGHTS = (7, 3, 1)

def mrz_value(c):
    if c == "<":
        return 0
    if c.isdigit():
        return int(c)
    if "A" <= c <= "Z":
        return ord(c) - ord("A") + 10
    raise ValueError(f"Invalid MRZ character: {c!r}")

def calc_check_digit(text):
    total = sum(mrz_value(c) * WEIGHTS[i % 3] for i, c in enumerate(text))
    return str(total % 10)

def human_date_to_mrz(value):
    if not value:
        return None
    try:
        return datetime.strptime(value.upper(), "%d %b %Y").strftime("%y%m%d")
    except ValueError:
        return None

def load_result(path):
    text = Path(path).read_text(encoding="utf-8").strip()
    return json.loads(text)

def normalize_name(value):
    return re.sub(r"\s+", " ", (value or "").strip().upper())

def add(results, status, check, detail):
    results.append({
        "status": status,
        "check": check,
        "detail": detail,
    })

def validate(data):
    results = []
    uncertain = set(data.get("uncertain_fields") or [])

    # ---------- ordinary fields ----------
    passport = data.get("passport_number")
    if passport is None:
        add(results, "WARN", "passport_number_present", "passport_number is null")
    elif re.fullmatch(r"[A-Z0-9]{1,9}", passport):
        add(results, "PASS", "passport_number_format", passport)
    else:
        add(results, "FAIL", "passport_number_format",
            f"invalid extracted value: {passport!r}")

    # ---------- MRZ structural validation ----------
    line1 = data.get("mrz_line_1")
    line2 = data.get("mrz_line_2")

    valid_line1 = isinstance(line1, str) and len(line1) == 44 and \
                  re.fullmatch(r"[A-Z0-9<]{44}", line1)

    valid_line2 = isinstance(line2, str) and len(line2) == 44 and \
                  re.fullmatch(r"[A-Z0-9<]{44}", line2)

    if valid_line1:
        add(results, "PASS", "mrz_line_1_structure", "44 valid MRZ characters")
    else:
        add(results, "FAIL", "mrz_line_1_structure",
            f"value={line1!r}, length={len(line1) if isinstance(line1,str) else None}")

    if valid_line2:
        add(results, "PASS", "mrz_line_2_structure", "44 valid MRZ characters")
    else:
        add(results, "FAIL", "mrz_line_2_structure",
            f"value={line2!r}, length={len(line2) if isinstance(line2,str) else None}")

    # ---------- line 1 cross-check ----------
    if valid_line1:
        mrz_doc_type = line1[0]
        mrz_issuer = line1[2:5]

        names = line1[5:].split("<<", 1)
        mrz_surname = names[0].replace("<", " ").strip()
        mrz_given = names[1].replace("<", " ").strip() if len(names) > 1 else ""

        comparisons = [
            ("document_type_vs_mrz", data.get("document_type"), mrz_doc_type),
            ("issuing_country_vs_mrz", data.get("issuing_country"), mrz_issuer),
            ("surname_vs_mrz", normalize_name(data.get("surname")),
             normalize_name(mrz_surname)),
            ("given_names_vs_mrz", normalize_name(data.get("given_names")),
             normalize_name(mrz_given)),
        ]

        for name, visible, mrz in comparisons:
            if visible == mrz:
                add(results, "PASS", name, f"{visible!r}")
            else:
                add(results, "CONFLICT", name,
                    f"visible={visible!r}, mrz={mrz!r}")

    # ---------- line 2 ICAO checks ----------
    if valid_line2:
        document_number = line2[0:9]
        document_cd = line2[9]

        nationality = line2[10:13]

        dob = line2[13:19]
        dob_cd = line2[19]

        sex = line2[20]

        expiry = line2[21:27]
        expiry_cd = line2[27]

        optional = line2[28:42]
        optional_cd = line2[42]

        composite_cd = line2[43]

        checks = [
            ("document_number_check",
             calc_check_digit(document_number), document_cd),

            ("date_of_birth_check",
             calc_check_digit(dob), dob_cd),

            ("expiry_date_check",
             calc_check_digit(expiry), expiry_cd),

            ("optional_data_check",
             calc_check_digit(optional), optional_cd),
        ]

        composite_source = (
            line2[0:10] +
            line2[13:20] +
            line2[21:43]
        )

        checks.append((
            "composite_check",
            calc_check_digit(composite_source),
            composite_cd
        ))

        for name, expected, actual in checks:
            if expected == actual:
                add(results, "PASS", name,
                    f"check digit={actual}")
            else:
                add(results, "FAIL", name,
                    f"expected={expected}, got={actual}")

        # Cross-check visible fields against MRZ.
        mrz_passport = document_number.replace("<", "")
        mrz_dob = dob
        mrz_expiry = expiry

        visible_dob = human_date_to_mrz(data.get("date_of_birth"))
        visible_expiry = human_date_to_mrz(data.get("expiry_date"))

        comparisons = [
            ("passport_number_vs_mrz", passport, mrz_passport),
            ("nationality_vs_mrz", data.get("nationality"), nationality),
            ("sex_vs_mrz", data.get("sex"), sex),
            ("date_of_birth_vs_mrz", visible_dob, mrz_dob),
            ("expiry_date_vs_mrz", visible_expiry, mrz_expiry),
        ]

        for name, visible, mrz in comparisons:
            if visible == mrz:
                add(results, "PASS", name, f"{visible!r}")
            else:
                add(results, "CONFLICT", name,
                    f"visible={visible!r}, mrz={mrz!r}")

    # ---------- uncertainty calibration ----------
    bad_fields = set()

    if not valid_line1:
        bad_fields.add("mrz_line_1")
    if not valid_line2:
        bad_fields.add("mrz_line_2")

    if passport is not None and not re.fullmatch(r"[A-Z0-9]{1,9}", passport):
        bad_fields.add("passport_number")

    unreported = sorted(bad_fields - uncertain)

    if unreported:
        add(results, "FAIL", "uncertainty_calibration",
            "model failed to mark these questionable fields uncertain: "
            + ", ".join(unreported))
    else:
        add(results, "PASS", "uncertainty_calibration",
            f"uncertain_fields={sorted(uncertain)}")

    # ---------- final verdict ----------
    statuses = [r["status"] for r in results]

    if "CONFLICT" in statuses and "FAIL" not in statuses:
        verdict = "CONFLICT_REVIEW"
    elif "FAIL" in statuses or "WARN" in statuses:
        verdict = "NEED_MORE_EVIDENCE"
    else:
        verdict = "ACCEPT_EXTRACTION"

    return verdict, results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python validator.py RESULT.json")

    data = load_result(sys.argv[1])
    verdict, results = validate(data)

    print()
    print("=" * 72)
    print("DETERMINISTIC VERDICT:", verdict)
    print("=" * 72)

    for r in results:
        print(f'{r["status"]:8} {r["check"]:30} {r["detail"]}')

    print()
