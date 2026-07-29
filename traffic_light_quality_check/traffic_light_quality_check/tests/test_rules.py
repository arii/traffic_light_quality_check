import pytest
from observesign.models import Task, Annotation
from observesign.rules import run_tax_rules, run_geo_rules, run_ovl_rules

def create_task(annotations, image_w=None, image_h=None):
    return Task(task_id="t1", annotations=annotations, image_width=image_w, image_height=image_h)

def test_tax_001_invalid_label():
    ann = Annotation(uuid="a1", label="invalid_label", geometry="box", left=0, top=0, width=10, height=10, attributes={
        "occlusion": "0%", "truncation": "0%", "background_color": "white"
    })
    task = create_task([ann])
    findings = run_tax_rules(task)
    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-001"

def test_tax_002_invalid_attributes():
    ann = Annotation(uuid="a1", label="traffic_control_sign", geometry="box", left=0, top=0, width=10, height=10, attributes={
        "occlusion": "invalid", "truncation": "0%", "background_color": "white"
    })
    task = create_task([ann])
    findings = run_tax_rules(task)
    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-002"
    assert "Invalid occlusion value" in findings[0].explanation

def test_tax_003_non_visible_face():
    ann = Annotation(uuid="a1", label="non_visible_face", geometry="box", left=0, top=0, width=10, height=10, attributes={
        "occlusion": "0%", "truncation": "0%", "background_color": "white"
    })
    task = create_task([ann])
    findings = run_tax_rules(task)
    assert len(findings) == 1
    assert findings[0].rule_id == "TAX-003"

def test_geo_001_out_of_bounds():
    ann = Annotation(uuid="a1", label="policy_sign", geometry="box", left=90, top=90, width=20, height=20, attributes={
        "occlusion": "0%", "truncation": "0%", "background_color": "white"
    })
    task = create_task([ann], image_w=100, image_h=100)
    findings = run_geo_rules(task)
    assert len(findings) == 1
    assert findings[0].rule_id == "GEO-001"

def test_geo_002_micro_box():
    ann = Annotation(uuid="a1", label="policy_sign", geometry="box", left=0, top=0, width=1, height=1, attributes={
        "occlusion": "0%", "truncation": "0%", "background_color": "white"
    })
    task = create_task([ann], image_w=100, image_h=100)
    findings = run_geo_rules(task)
    assert len(findings) == 1
    assert findings[0].rule_id == "GEO-002"

def test_geo_003_giant_box():
    ann = Annotation(uuid="a1", label="policy_sign", geometry="box", left=0, top=0, width=95, height=95, attributes={
        "occlusion": "0%", "truncation": "0%", "background_color": "white"
    })
    task = create_task([ann], image_w=100, image_h=100)
    findings = run_geo_rules(task)
    assert len(findings) == 1
    assert findings[0].rule_id == "GEO-003"

def test_ovl_001_duplicate():
    a1 = Annotation(uuid="a1", label="policy_sign", geometry="box", left=10, top=10, width=50, height=50, attributes={})
    a2 = Annotation(uuid="a2", label="policy_sign", geometry="box", left=11, top=11, width=49, height=49, attributes={})
    task = create_task([a1, a2])
    findings = run_ovl_rules(task)
    # Check if there is an OVL-001 finding (could also have OVL-002 if fully contained)
    ovl_001_findings = [f for f in findings if f.rule_id == "OVL-001"]
    assert len(ovl_001_findings) >= 1

def test_ovl_002_containment():
    a1 = Annotation(uuid="a1", label="policy_sign", geometry="box", left=0, top=0, width=100, height=100, attributes={})
    a2 = Annotation(uuid="a2", label="policy_sign", geometry="box", left=10, top=10, width=10, height=10, attributes={})
    task = create_task([a1, a2])
    findings = run_ovl_rules(task)
    # OVL-002 only
    ovl_002_findings = [f for f in findings if f.rule_id == "OVL-002"]
    assert len(ovl_002_findings) == 1
    assert ovl_002_findings[0].annotation_id == "a2"
