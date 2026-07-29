from traffic_light.models import Task, Annotation, BoundingBox
from traffic_light.rules import audit_task
from traffic_light.rules import QualityConfig

def test_engine_valid_task():
    ann = Annotation(id="1", label="traffic_control_sign", box=BoundingBox(10, 10, 50, 50), attributes={"background_color": "white"})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann])
    findings = audit_task(task)
    assert len(findings) == 0

def test_engine_multiple_findings():
    # Out of bounds AND invalid label
    ann = Annotation(id="1", label="invalid_label", box=BoundingBox(-10, 10, 50, 50), attributes={})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann])
    findings = audit_task(task)
    assert len(findings) == 2
    rule_ids = [f.rule_id for f in findings]
    assert "TAX-001" in rule_ids
    assert "GEO-001" in rule_ids
