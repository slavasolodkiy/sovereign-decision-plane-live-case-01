"""Optional GCS storage witness. Python stdlib + authenticated gcloud; no mock mode."""
import argparse
import hashlib
import http.client
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def make_receipt(packet_bytes, source_commit):
    """Project only synthetic case decisions; omit raw inputs and model responses."""
    packet = json.loads(packet_bytes)
    if packet["case"]["synthetic_data"] is not True:
        raise ValueError("This demonstrator accepts synthetic evidence only")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("An exact source Git commit is required")
    case_id = packet["case"]["case_id"]
    allowed = {"SDP-PASSPORT-T1B", "SDP-PASSPORT-GREEN-CONTROL"}
    if case_id not in allowed:
        raise ValueError("Unsupported public synthetic case")
    op = packet["operational_decision"]
    if op["ai_authorised_to_override"] is not False:
        raise ValueError("Unexpected authority boundary")
    expected = ("accept_extraction", "ALLOW") if case_id.endswith("CONTROL") else (
        "request_better_evidence", "ESCALATE_TO_HUMAN")
    if (packet["formal_logic"]["decision"], op["outcome"]) != expected:
        raise ValueError("Unexpected case outcome")
    return {
        "schema": "sdp-storage-receipt-v1",
        "case_id": case_id,
        "synthetic_data": True,
        "source_commit": source_commit,
        "source_packet_sha256": hashlib.sha256(packet_bytes).hexdigest(),
        "evidence_origin": "recorded_local_run",
        "control_type": "prevalidated_synthetic_control" if case_id.endswith("CONTROL")
                        else "captured_nemotron_candidate",
        "formal_decision": expected[0],
        "operational_outcome": expected[1],
        "ai_authorised_to_override": False,
        "scope": "Storage receipt only; does not validate decision correctness or establish immutable retention.",
    }


def cloud_request(method, path, token, payload=None):
    # Fixed host and no redirects: credentials never follow an arbitrary URL.
    conn = http.client.HTTPSConnection("storage.googleapis.com", timeout=30)
    try:
        conn.request(method, path, body=payload, headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        })
        response = conn.getresponse()
        return response.status, response.read(1024 * 1024)
    finally:
        conn.close()


def upload_receipt(receipt, bucket, token, request=cloud_request):
    """Create without overwrite and verify exact generation by downloading bytes."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,220}[a-z0-9]", bucket):
        raise ValueError("Invalid bucket name")
    payload = canonical(receipt)
    digest = hashlib.sha256(payload).hexdigest()
    name = "sdp-witness/" + digest + ".json"
    base = "/storage/v1/b/" + quote(bucket, safe="") + "/o/" + quote(name, safe="")
    path = "/upload/storage/v1/b/" + quote(bucket, safe="") + "/o?" + urlencode({
        "uploadType": "media", "name": name, "ifGenerationMatch": "0"})
    status, body = request("POST", path, token, payload)
    created = status in (200, 201)
    if status == 412:
        # Existing content-addressed object is never overwritten.
        status, body = request("GET", base, token)
    if status not in (200, 201):
        raise RuntimeError(f"GCS upload/metadata failed (HTTP {status}); no verified witness")
    metadata = json.loads(body)
    if metadata.get("bucket") != bucket or metadata.get("name") != name:
        raise RuntimeError("GCS object identity mismatch")
    generation = str(metadata.get("generation", ""))
    if not generation.isdigit() or int(generation) <= 0:
        raise RuntimeError("Missing GCS object generation")
    status, downloaded = request("GET", base + "?" + urlencode({
        "alt": "media", "generation": generation, "ifGenerationMatch": generation}), token)
    if status != 200 or downloaded != payload:
        raise RuntimeError("GCS readback failed or bytes differ; upload may exist but is not verified")
    return {
        "status": "GCS_READBACK_VERIFIED", "created_this_run": created,
        "bucket": bucket, "object": name, "generation": generation,
        "gcs_time_created": metadata.get("timeCreated"),
        "receipt_sha256": digest, "readback_sha256": hashlib.sha256(downloaded).hexdigest(),
        "bytes": len(payload), "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "retention_claim": "none", "decision_correctness_claim": "none",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--bucket", help="Existing authorized GCS bucket; omission prepares locally only")
    parser.add_argument("--result", type=Path, help="New file for successful live readback report")
    args = parser.parse_args()
    if args.result and args.result.exists():
        parser.error("Result path already exists; choose a new path to avoid stale success reports")
    if args.bucket and not args.result:
        parser.error("--result required for live upload")
    receipt = make_receipt(args.packet.read_bytes(), args.source_commit)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes(canonical(receipt))
    if not args.bucket:
        print("LOCAL_RECEIPT_PREPARED (no GCP action)")
        return
    gcloud = shutil.which("gcloud")
    if not gcloud:
        parser.exit(1, "Authenticated gcloud is required; use Google Cloud Shell or install gcloud.\n")
    auth = subprocess.run([gcloud, "auth", "print-access-token", "--quiet"],
                          capture_output=True, text=True, timeout=30)
    if auth.returncode or not auth.stdout.strip():
        parser.exit(1, "gcloud authentication failed; no GCS action completed.\n")
    result = upload_receipt(receipt, args.bucket, auth.stdout.strip())
    args.result.parent.mkdir(parents=True, exist_ok=True)
    with args.result.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
