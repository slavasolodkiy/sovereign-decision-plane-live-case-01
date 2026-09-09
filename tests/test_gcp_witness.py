"""Offline contract tests; never reported as a real GCP execution."""
import hashlib
import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit

from adapters.gcp_witness import canonical, make_receipt, upload_receipt

ROOT = Path(__file__).resolve().parents[1]
PACKET = (ROOT / "evidence/SDP-PASSPORT-T1B-evidence.json").read_bytes()
COMMIT = "6d60a418725d313c66fb1eff3d40aa8ef2f4f724"


class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.receipt = make_receipt(PACKET, COMMIT)
        self.data = canonical(self.receipt)
        self.name = "sdp-witness/" + hashlib.sha256(self.data).hexdigest() + ".json"
        self.metadata = json.dumps({"bucket": "test-bucket", "name": self.name,
                                    "generation": "123", "timeCreated": "2026-09-09T00:00:00Z"}).encode()

    def test_receipt_is_repeatable_and_excludes_source_fields(self):
        packet = json.loads(PACKET)
        packet["passport_number"] = "DO-NOT-UPLOAD"
        result = make_receipt(json.dumps(packet).encode(), COMMIT)
        self.assertNotIn("DO-NOT-UPLOAD", canonical(result).decode())
        self.assertEqual(self.data, canonical(make_receipt(PACKET, COMMIT)))
        self.assertNotEqual(result["source_packet_sha256"], self.receipt["source_packet_sha256"])

    def test_rejects_non_synthetic_and_authority_override(self):
        for key in ("synthetic", "override", "outcome"):
            p = json.loads(PACKET)
            if key == "synthetic": p["case"]["synthetic_data"] = False
            if key == "override": p["operational_decision"]["ai_authorised_to_override"] = True
            if key == "outcome": p["operational_decision"]["outcome"] = "ALLOW"
            with self.assertRaises(ValueError): make_receipt(json.dumps(p).encode(), COMMIT)

    def test_live_protocol_uses_create_only_and_generation_readback(self):
        calls = []
        def request(method, path, token, payload=None):
            calls.append((method, path))
            query = parse_qs(urlsplit(path).query)
            if method == "POST":
                self.assertEqual(query["ifGenerationMatch"], ["0"])
                self.assertEqual(payload, self.data)
                return 200, self.metadata
            self.assertEqual(query["generation"], ["123"])
            self.assertEqual(query["ifGenerationMatch"], ["123"])
            return 200, self.data
        result = upload_receipt(self.receipt, "test-bucket", "test-token", request)
        self.assertTrue(result["created_this_run"])
        self.assertEqual(result["receipt_sha256"], result["readback_sha256"])
        self.assertEqual(len(calls), 2)

    def test_existing_object_is_verified_without_overwrite(self):
        replies = iter([(412, b""), (200, self.metadata), (200, self.data)])
        result = upload_receipt(self.receipt, "test-bucket", "test-token",
                                lambda *args: next(replies))
        self.assertFalse(result["created_this_run"])

    def test_corrupt_readback_and_denied_access_fail_closed(self):
        for replies in ([(200, self.metadata), (200, b"changed")], [(403, b"denied")],
                        [(200, b'{"generation":"123","bucket":"other","name":"other"}')]):
            responses = iter(replies)
            with self.assertRaises(RuntimeError):
                upload_receipt(self.receipt, "test-bucket", "test-token", lambda *args: next(responses))


if __name__ == "__main__":
    unittest.main()
