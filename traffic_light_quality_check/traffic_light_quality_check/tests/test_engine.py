import pytest
from observesign.engine import QualityEngine

def test_engine_empty_task():
    engine = QualityEngine()
    task_data = {
        "task_id": "t1",
        "response": {
            "annotations": []
        }
    }
    findings = engine.evaluate_tasks_from_dicts([task_data])
    assert len(findings) == 0

def test_engine_evaluates_rules():
    engine = QualityEngine()
    task_data = {
        "task_id": "t1",
        "response": {
            "annotations": [
                {
                    "uuid": "a1",
                    "label": "invalid_label",
                    "geometry": "box",
                    "left": 0, "top": 0, "width": 1, "height": 1,
                    "attributes": {}
                }
            ]
        }
    }
    findings = engine.evaluate_tasks_from_dicts([task_data])
    # Expect TAX-001 (invalid label), TAX-002 (missing attributes), GEO-002 (micro box)
    rule_ids = [f.rule_id for f in findings]
    assert "TAX-001" in rule_ids
    assert "TAX-002" in rule_ids
    assert "GEO-002" in rule_ids
