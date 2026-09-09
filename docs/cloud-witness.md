# Optional Google Cloud Storage witness

Status: **real GCS upload and generation-specific readback verified on 9 September
2026, 08:32 UTC**, using this adapter in Google Cloud Shell. Five offline contract
tests also passed locally and in Cloud Shell. The original model inference was
not repeated for this storage experiment.

## Recorded live result

- Stored receipt size: 545 bytes.
- GCS generation: `1788942747393502`.
- GCS creation time: `2026-09-09T08:32:27.399Z`.
- Readback verified: `2026-09-09T08:32:28.058972+00:00`.
- Receipt and readback SHA-256:
  `771cbab54cd029e8c65ad520e1bdc72ce219cc14eaeb6a491edef8bed1999381`.
- Source evidence commit: `6d60a418725d313c66fb1eff3d40aa8ef2f4f724`.
- Bucket configuration: Standard, us-east1, public access prevention enforced,
  uniform bucket-level access, default soft delete, no retention lock.

The full operational report is kept locally because it contains the bucket
identifier. The [public receipt](evidence/cloud-witness-receipt.json) can be hashed
independently; the [sanitized execution report](evidence/cloud-witness-result.json)
records the observed live result with the bucket identifier omitted. These recorded
values are an author's experiment report, not an independently signed attestation.
The bucket remains private.

The local Nemotron / Python / SWI-Prolog / OPA decision pipeline is unchanged.
This adapter projects a small receipt from an already recorded synthetic evidence
packet, hashes the exact receipt bytes, uploads them to Google Cloud Storage, then
downloads the returned object generation and compares the bytes and SHA-256.
The receipt contains the case identifier, source packet hash, source Git commit,
formal/operational outcomes and authority flag. It excludes document images,
extracted passport fields, model responses, credentials and runtime logs.

This is storage witnessing, not independent decision validation. SHA-256 binds
bytes; it does not prove their truth, authorship, original execution time or legal
correctness. A successful upload does not establish WORM retention. The adapter
uses create-only `ifGenerationMatch=0` and never overwrites an existing object.
It verifies an existing content-addressed object on a repeated invocation and
reports `created_this_run=false`. Privileged deletion remains possible.

## Local tests

```sh
python3 -m unittest discover -s tests -p 'test_gcp_witness.py' -v
```

These use test doubles at the HTTP boundary. There is no production mock mode
and these tests do not demonstrate GCP execution.

## Real execution

Use an authenticated `gcloud` session, for example Google Cloud Shell. The
adapter uses Python's standard library; no service-account key is needed.
Use an existing authorized private bucket with public access prevention and
uniform bucket-level access. The principal needs object create/get permissions.
Bucket creation, IAM changes, billing enablement and public access are outside
this adapter. Storage/operation charges follow the account's GCP terms.

Run from the repository root, substituting your actual bucket name:

```sh
python3 adapters/gcp_witness.py \
  --packet evidence/SDP-PASSPORT-T1B-evidence.json \
  --source-commit 6d60a418725d313c66fb1eff3d40aa8ef2f4f724 \
  --receipt local-witness/receipt.json \
  --bucket YOUR_EXISTING_BUCKET \
  --result local-witness/gcs-result.json
```

Omit `--bucket` and `--result` to prepare only the local receipt. This prints
`LOCAL_RECEIPT_PREPARED`, never a cloud-success status. Do not overwrite an old
result report; choose a new path for each run. If upload succeeds but readback
fails, the object may exist; do not claim a verified witness. Re-run to verify
that existing object after resolving the error.

## Publish evidence only after live success

The success report records bucket/object, generation, GCS creation time,
verification time, byte count and matching local/download hashes. Review account
and resource identifiers before publishing. Keep credentials private; the adapter
does not print or save tokens. A screenshot of the object and successful readback
can complement the report. Do not grant public bucket access for the contest.

Accurate description after verification: "The local decision pipeline exports a
receipt to Google Cloud Storage. We verified a real upload by reading the exact
object generation back and matching its SHA-256. Decision authority remains in
the local verification and policy stack."

References: [GCS insert](https://docs.cloud.google.com/storage/docs/json_api/v1/objects/insert),
[GCS get](https://docs.cloud.google.com/storage/docs/json_api/v1/objects/get),
[preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions).
