import hashlib
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CASE_ID = "SDP-PASSPORT-T1B"
MODEL_ID = "nemotron3:33b-q4_K_M"


def sha256_file(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_record(relative_path):
    path = ROOT / relative_path
    return {
        "path": str(relative_path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size
    }


# ------------------------------------------------------------
# 1. Load structured input created from real validator + FOL run
# ------------------------------------------------------------

opa_input_path = ROOT / "input/t1b_opa_input.json"
opa_input = json.loads(opa_input_path.read_text())


# ------------------------------------------------------------
# 2. Execute OPA again NOW and capture actual machine output
# ------------------------------------------------------------

cmd = [
    "opa", "eval",
    "--format=json",
    "--data", str(ROOT / "policy/passport_gate.rego"),
    "--input", str(opa_input_path),
    "data.sovereign_decision_plane.passport.decision"
]

raw_opa = subprocess.check_output(cmd, text=True)
opa_envelope = json.loads(raw_opa)

try:
    opa_decision = opa_envelope["result"][0]["expressions"][0]["value"]
except Exception as e:
    raise SystemExit(f"Could not extract OPA decision: {e}")

opa_decision_path = ROOT / "evidence/SDP-PASSPORT-T1B-opa-decision.json"
opa_decision_path.write_text(
    json.dumps(opa_decision, indent=2) + "\n"
)


# ------------------------------------------------------------
# 3. Obtain actual local model metadata from Ollama
# ------------------------------------------------------------

model_metadata = {
    "model_id": MODEL_ID,
    "ollama_model_digest": None,
    "quantization": None,
    "context_length": None
}

try:
    ollama_ip = subprocess.check_output(
        [
            "kubectl",
            "-n", "ollamaserver-shared",
            "get", "svc", "ollama",
            "-o", "jsonpath={.spec.clusterIP}"
        ],
        text=True
    ).strip()

    with urllib.request.urlopen(
        f"http://{ollama_ip}:11434/api/tags",
        timeout=10
    ) as r:
        tags = json.load(r)

    for model in tags.get("models", []):
        if model.get("name") == MODEL_ID:
            model_metadata["ollama_model_digest"] = model.get("digest")

            details = model.get("details") or {}
            model_metadata["quantization"] = details.get("quantization_level")

            # Some Ollama builds expose context length elsewhere,
            # so we do not invent it if absent.
            if "context_length" in model:
                model_metadata["context_length"] = model["context_length"]
            break

except Exception as e:
    model_metadata["metadata_lookup_note"] = str(e)


# ------------------------------------------------------------
# 4. Collect only hashes that actually exist
# ------------------------------------------------------------

artifact_paths = [
    "input/specimen_passport_valid.png",
    "input/t1b_opa_input.json",
    "perception/T1b_api_result.json",
    "verification/validator.py",
    "logic/t1b_facts.pl",
    "logic/policy.pl",
    "policy/passport_gate.rego",
    "evidence/SDP-PASSPORT-T1B-opa-decision.json",
]

if (ROOT / "artifacts/final_explanation.json").exists():
    artifact_paths.append("artifacts/final_explanation.json")

artifacts = {
    Path(p).stem: artifact_record(p)
    for p in artifact_paths
}


# ------------------------------------------------------------
# 5. Runtime versions
# ------------------------------------------------------------

opa_version = subprocess.check_output(
    ["opa", "version"],
    text=True
).strip()

try:
    swipl_version = subprocess.check_output(
        ["swipl", "--version"],
        text=True
    ).strip()
except Exception:
    swipl_version = None


# ------------------------------------------------------------
# 6. Evidence packet
# ------------------------------------------------------------

packet = {
    "artifact_type": "sovereign_decision_plane_evidence_packet",
    "artifact_version": "0.1.0",

    "generated_at_utc": datetime.now(timezone.utc).isoformat(),

    "case": {
        "case_id": CASE_ID,
        "case_type": "passport_evidence_integrity",
        "synthetic_data": True,
        "environment": "local_olares_demonstrator"
    },

    "architecture": {
        "perception": "Nemotron 3 Nano Omni via Ollama",
        "deterministic_verification": "Python ICAO/MRZ validator",
        "formal_logic": "SWI-Prolog",
        "institutional_policy": "Open Policy Agent / Rego",
        "explanation": "Nemotron, explanation-only",
        "ai_authorised_to_override": False
    },

    "model": model_metadata,

    "verification": opa_input["verification"],

    "formal_logic": opa_input["formal_logic"],

    "operational_decision": opa_decision,

    "runtime": {
        "opa": opa_version,
        "swipl": swipl_version
    },

    "artifacts": artifacts,

    "reproducibility": {
        "opa_check": "opa check policy/passport_gate.rego",
        "opa_eval": (
            "opa eval --format=pretty "
            "--data policy/passport_gate.rego "
            "--input input/t1b_opa_input.json "
            "'data.sovereign_decision_plane.passport.decision'"
        )
    },

    "integrity_note": (
        "This is an illustrative, synthetic, locally executed technical "
        "demonstrator. It is not a production identity decision, legal opinion, "
        "regulatory filing, regulatory approval, or claim of compliance. "
        "The evidence packet records the executed control path and artifact hashes."
    )
}

packet_path = ROOT / "evidence/SDP-PASSPORT-T1B-evidence.json"
packet_path.write_text(
    json.dumps(packet, indent=2) + "\n"
)


# ------------------------------------------------------------
# 7. SHA-256 manifest
# ------------------------------------------------------------

manifest_lines = []

for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue

    rel = p.relative_to(ROOT)

    # Do not recursively hash the manifest itself.
    if rel == Path("artifacts/checksums.sha256"):
        continue

    manifest_lines.append(
        f"{sha256_file(p)}  {rel}"
    )

manifest = ROOT / "artifacts/checksums.sha256"
manifest.write_text("\n".join(manifest_lines) + "\n")


# ------------------------------------------------------------
# 8. Human-readable success summary
# ------------------------------------------------------------

print()
print("============================================================")
print("SOVEREIGN DECISION PLANE — LIVE CASE 01")
print("============================================================")
print("CASE:", CASE_ID)
print("FOL:", packet["formal_logic"]["decision"])
print("OPA:", packet["operational_decision"]["outcome"])
print(
    "AI OVERRIDE:",
    packet["operational_decision"]["ai_authorised_to_override"]
)
print()
print("EVIDENCE PACKET:")
print(packet_path)
print()
print("SHA256:")
print(sha256_file(packet_path))
print("============================================================")
