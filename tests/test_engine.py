from src.observesign.models import Task, Annotation, BoundingBox
from src.observesign.engine import audit_task, audit_tasks
from src.observesign.rules import QualityConfig

def test_audit_task_no_findings():
    task = Task(
        id="t1",
        image_url="test.jpg",
        image_width=1000,
        image_height=1000,
        annotations=[
            Annotation("a1", "traffic_control_sign", BoundingBox(10, 10, 50, 50), {"occlusion": "0%", "truncation": "0%", "background_color": "red"}),
            Annotation("a2", "non_visible_face", BoundingBox(100, 100, 50, 50), {"occlusion": "25%", "truncation": "0%", "background_color": "not_applicable"})
        ]
    )
    findings = audit_task(task, QualityConfig())
    assert len(findings) == 0

def test_audit_task_multiple_findings():
    task = Task(
        id="t1",
        image_url="test.jpg",
        image_width=100,
        image_height=100,
        annotations=[
            # This triggers TAX-001 (bad label), TAX-004 (wrong background for label), GEO-001 (out of bounds)
            Annotation("a1", "bad_label", BoundingBox(-10, 10, 50, 50), {"background_color": "not_applicable"})
        ]
    )
    findings = audit_task(task, QualityConfig())
    rule_ids = {f.rule_id for f in findings}
    assert "TAX-001" in rule_ids
    assert "TAX-004" in rule_ids
    assert "GEO-001" in rule_ids

def test_audit_tasks():
    t1 = Task(id="t1", image_url="", image_width=100, image_height=100, annotations=[])
    # Giant box
    t2 = Task(id="t2", image_url="", image_width=100, image_height=100, annotations=[
        Annotation("a2", "traffic_control_sign", BoundingBox(0,0,100,100), {"background_color": "red"})
    ])

    results = audit_tasks([t1, t2], QualityConfig(giant_box_area_ratio=0.8))
    assert len(results["t1"]) == 0
    assert len(results["t2"]) > 0
    assert any(f.rule_id == "GEO-003" for f in results["t2"])
