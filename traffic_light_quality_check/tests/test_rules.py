from traffic_light.models import Task, Annotation, BoundingBox
from traffic_light.rules import (
    QualityConfig,
    check_invalid_labels,
    check_invalid_attributes,
    check_out_of_bounds,
    check_micro_boxes,
    check_giant_boxes,
    check_duplicate_boxes,
    check_suspicious_containment
)

config = QualityConfig()

def test_invalid_label():
    ann = Annotation(id="1", label="invalid_label", box=BoundingBox(10, 10, 50, 50), attributes={})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann])
    findings = check_invalid_labels(task, config)
    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-001"

    ann_valid = Annotation(id="2", label="traffic_control_sign", box=BoundingBox(10, 10, 50, 50), attributes={})
    task_valid = Task(id="t2", image_url="", image_width=1000, image_height=1000, annotations=[ann_valid])
    assert len(check_invalid_labels(task_valid, config)) == 0

def test_invalid_attributes():
    ann = Annotation(id="1", label="traffic_control_sign", box=BoundingBox(10, 10, 50, 50), attributes={"invalid_key": "val"})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann])
    findings = check_invalid_attributes(task, config)
    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-002"

    ann_valid = Annotation(id="2", label="traffic_control_sign", box=BoundingBox(10, 10, 50, 50), attributes={"background_color": "white"})
    task_valid = Task(id="t2", image_url="", image_width=1000, image_height=1000, annotations=[ann_valid])
    assert len(check_invalid_attributes(task_valid, config)) == 0

def test_giant_box():
    ann = Annotation(id="1", label="traffic_control_sign", box=BoundingBox(0, 0, 950, 950), attributes={})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann])
    findings = check_giant_boxes(task, config)
    assert len(findings) == 1
    assert findings[0].rule_id == "GEO-003"

def test_micro_box():
    ann = Annotation(id="1", label="traffic_control_sign", box=BoundingBox(10, 10, 2, 2), attributes={})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann])
    findings = check_micro_boxes(task, config)
    assert len(findings) == 1
    assert findings[0].rule_id == "GEO-002"

def test_duplicate_boxes():
    ann1 = Annotation(id="1", label="traffic_control_sign", box=BoundingBox(10, 10, 50, 50), attributes={})
    ann2 = Annotation(id="2", label="traffic_control_sign", box=BoundingBox(11, 11, 49, 49), attributes={})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann1, ann2])
    findings = check_duplicate_boxes(task, config)
    assert len(findings) == 2  # One for each annotation
    assert findings[0].rule_id == "OVL-001"

def test_suspicious_containment():
    ann_outer = Annotation(id="1", label="traffic_control_sign", box=BoundingBox(10, 10, 100, 100), attributes={})
    ann_inner = Annotation(id="2", label="traffic_control_sign", box=BoundingBox(20, 20, 10, 10), attributes={})
    task = Task(id="t1", image_url="", image_width=1000, image_height=1000, annotations=[ann_outer, ann_inner])
    findings = check_suspicious_containment(task, config)
    assert len(findings) == 1
    assert findings[0].rule_id == "OVL-002"
    assert findings[0].annotation_id == "2"
