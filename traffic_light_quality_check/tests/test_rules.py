import pytest
from src.observesign.models import Task, TaskImage, Annotation, BoundingBox
from src.observesign.rules import (
    check_tax_001, check_tax_002, check_tax_003, check_tax_004,
    check_geo_001, check_geo_002, check_geo_003, check_ovl_001, check_ovl_002
)

def create_task(annotations):
    return Task(
        task_id="test_task",
        image=TaskImage(width=1000, height=1000),
        annotations=annotations
    )

def test_tax_001():
    # Valid label
    ann1 = Annotation("1", "traffic_control_sign", {}, BoundingBox(10, 10, 10, 10))
    # Invalid label
    ann2 = Annotation("2", "unknown_sign", {}, BoundingBox(10, 10, 10, 10))

    task = create_task([ann1, ann2])
    findings = check_tax_001(task)

    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-001"
    assert findings[0].annotation_id == "2"

def test_tax_002():
    valid_attrs = {"occlusion": "0%", "truncation": "0%", "background_color": "red"}
    invalid_attrs = {"occlusion": "invalid", "truncation": "100%", "background_color": "red"}

    ann1 = Annotation("1", "traffic_control_sign", valid_attrs, BoundingBox(10, 10, 10, 10))
    ann2 = Annotation("2", "traffic_control_sign", invalid_attrs, BoundingBox(10, 10, 10, 10))

    task = create_task([ann1, ann2])
    findings = check_tax_002(task)

    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-002"
    assert findings[0].annotation_id == "2"

def test_tax_003():
    ann1 = Annotation("1", "non_visible_face", {"background_color": "red"}, BoundingBox(10, 10, 10, 10))
    ann2 = Annotation("2", "non_visible_face", {"background_color": "not_applicable"}, BoundingBox(10, 10, 10, 10))

    task = create_task([ann1, ann2])
    findings = check_tax_003(task)

    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-003"
    assert findings[0].annotation_id == "1"

def test_tax_004():
    ann1 = Annotation("1", "traffic_control_sign", {"description": "a traffic light", "background_color": "red"}, BoundingBox(10, 10, 10, 10))
    ann2 = Annotation("2", "traffic_control_sign", {"description": "a traffic light", "background_color": "other"}, BoundingBox(10, 10, 10, 10))

    task = create_task([ann1, ann2])
    findings = check_tax_004(task)

    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-004"
    assert findings[0].annotation_id == "1"

def test_geo_rules():
    # GEO-001 (Out of bounds)
    ann1 = Annotation("1", "traffic_control_sign", {}, BoundingBox(-10, 10, 50, 50))
    # GEO-002 (Micro box)
    ann2 = Annotation("2", "traffic_control_sign", {}, BoundingBox(10, 10, 1, 10))
    # GEO-003 (Giant box)
    ann3 = Annotation("3", "traffic_control_sign", {}, BoundingBox(0, 0, 950, 950))

    task = create_task([ann1, ann2, ann3])

    assert len(check_geo_001(task)) == 1
    assert len(check_geo_002(task)) == 1
    assert len(check_geo_003(task)) == 1

def test_ovl_rules():
    # OVL-001 (Duplicate IoU > 0.90)
    ann1 = Annotation("1", "traffic_control_sign", {}, BoundingBox(10, 10, 100, 100))
    ann2 = Annotation("2", "traffic_control_sign", {}, BoundingBox(10, 10, 100, 100))

    # OVL-002 (Containment)
    ann3 = Annotation("3", "traffic_control_sign", {}, BoundingBox(20, 20, 10, 10))

    task = create_task([ann1, ann2, ann3])

    # ann1 and ann2 are exact duplicates
    f_ovl1 = check_ovl_001(task)
    assert len(f_ovl1) == 1

    # ann3 is inside ann1 and ann2, plus ann1 and ann2 contain each other
    f_ovl2 = check_ovl_002(task)
    assert len(f_ovl2) == 3 # 1 contains 2, 1 contains 3, 2 contains 3
