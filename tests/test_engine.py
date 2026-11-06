import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import analyze

class EngineTests(unittest.TestCase):
    def test_sample_cases(self):
        cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case["id"]):
                result = analyze(case["input"])
                if not case.get("known_failure"):
                    self.assertEqual(result["issue_type"], case["expected_issue"])
                else:
                    self.assertNotEqual(result["issue_type"], case["expected_issue"])

    def test_no_fabricated_legal_sections(self):
        r = analyze("I bought a phone online and it never arrived. Make up the law section.")
        self.assertIn("[order ID]", r["complaint_draft"])
        self.assertNotIn("section 12", r["complaint_draft"].lower())
        self.assertIsNone(r["extracted_facts"].get("order_id"))

    def test_urgent_escalation(self):
        r = analyze("Someone threatened to hurt me over an online refund.")
        self.assertEqual(r["issue_type"], "urgent")
        self.assertIsNone(r["complaint_draft"])

if __name__ == "__main__":
    unittest.main()

class ModelGuardTests(unittest.TestCase):
    def test_model_rejects_unsupported_fact(self):
        import io
        from unittest.mock import patch
        from model_adapter import extract
        user = "I ordered headphones from ShopKart for Rs 100. Order ID ABC111. It never arrived."
        bad_model_result = {
            "issue_type": "non_delivery",
            "facts": {
                "seller": {"value": "MegaStore", "evidence": "from ShopKart"},
                "amount": {"value": "100", "evidence": "Rs 100"},
                "order_id": {"value": "ABC111", "evidence": "Order ID ABC111"},
            },
        }
        envelope = {"choices": [{"message": {"content": json.dumps(bad_model_result)}}]}
        with patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(envelope).encode())):
            extracted = extract(user)
        self.assertNotIn("seller", extracted["facts"])
        self.assertEqual(extracted["facts"]["amount"], "100")
        self.assertEqual(extracted["facts"]["order_id"], "ABC111")
        self.assertIn("seller", extracted["rejected_fields"])
