"""Reproduce raw, unedited results and a deterministic test summary.
python run_cases.py
"""
import json
from pathlib import Path
from engine import analyze

root = Path(__file__).parent
cases = json.loads((root / "cases.json").read_text(encoding="utf-8"))
out = root / "raw_outputs"
out.mkdir(exist_ok=True)
results = []
for case in cases:
    result = analyze(case["input"], use_model=False)
    record = {"test_id": case["id"], "input": case["input"], "output": result}
    (out / f"{case['id']}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    results.append({"test_id": case["id"], "expected": case["expected_issue"],
                    "actual": result["issue_type"], "match": case["expected_issue"] == result["issue_type"],
                    "model_status": result["model_status"]})
(out / "test_summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
