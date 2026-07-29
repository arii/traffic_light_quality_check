from src.observesign.models import Task, Annotation, BoundingBox
from src.observesign.rules import (
    QualityConfig,
    check_invalid_attributes,
    check_background_color,
    check_out_of_bounds,
    check_micro_boxes,
    check_giant_boxes,
    check_duplicate_boxes,
    check_suspicious_containment
)

def create_task(annotations) -> Task:
    return Task(
        id="test_task",
        image_url="test.jpg",
        image_width=1000,
        image_height=1000,
        annotations=annotations
    )

def test_check_invalid_attributes():
    config = QualityConfig()

    # Valid
    t1 = create_task([
        Annotation("1", "traffic_control_sign", BoundingBox(0,0,10,10), {"occlusion": "0%", "truncation": "0%"})
    ])
    assert not check_invalid_attributes(t1, config)

    # Invalid label
    t2 = create_task([
        Annotation("2", "bad_label", BoundingBox(0,0,10,10), {})
    ])
    f2 = check_invalid_attributes(t2, config)
    assert len(f2) == 1
    assert f2[0].rule_id == "TAX-001"

    # Invalid occlusion
    t3 = create_task([
        Annotation("3", "traffic_control_sign", BoundingBox(0,0,10,10), {"occlusion": "30%", "truncation": "0%"})
    ])
    f3 = check_invalid_attributes(t3, config)
    assert len(f3) == 1
    assert f3[0].rule_id == "TAX-002"

def test_check_background_color():
    config = QualityConfig()

    # Valid
    t1 = create_task([
        Annotation("1", "traffic_control_sign", BoundingBox(0,0,10,10), {"background_color": "red"}),
        Annotation("2", "non_visible_face", BoundingBox(0,0,10,10), {"background_color": "not_applicable"})
    ])
    assert not check_background_color(t1, config)

    # Invalid background color value
    t2 = create_task([
        Annotation("3", "traffic_control_sign", BoundingBox(0,0,10,10), {"background_color": "magenta"})
    ])
    f2 = check_background_color(t2, config)
    assert len(f2) == 1
    assert f2[0].rule_id == "TAX-003"

    # not_applicable used for wrong label
    t3 = create_task([
        Annotation("4", "traffic_control_sign", BoundingBox(0,0,10,10), {"background_color": "not_applicable"})
    ])
    f3 = check_background_color(t3, config)
    assert len(f3) == 1
    assert f3[0].rule_id == "TAX-004"

def test_check_out_of_bounds():
    config = QualityConfig()
    t_valid = create_task([Annotation("1", "x", BoundingBox(0,0,100,100), {})])
    assert not check_out_of_bounds(t_valid, config)

    t_invalid = create_task([Annotation("2", "x", BoundingBox(-10,0,100,100), {})])
    assert len(check_out_of_bounds(t_invalid, config)) == 1

def test_check_micro_boxes():
    config = QualityConfig(micro_box_width=5, micro_box_height=5, micro_box_area=25)
    t_valid = create_task([Annotation("1", "x", BoundingBox(0,0,10,10), {})])
    assert not check_micro_boxes(t_valid, config)

    t_invalid = create_task([Annotation("2", "x", BoundingBox(0,0,4,4), {})])
    assert len(check_micro_boxes(t_invalid, config)) == 1

def test_check_giant_boxes():
    config = QualityConfig(giant_box_area_ratio=0.8)
    t_valid = create_task([Annotation("1", "x", BoundingBox(0,0,500,500), {})]) # 0.25 ratio
    assert not check_giant_boxes(t_valid, config)

    t_invalid = create_task([Annotation("2", "x", BoundingBox(0,0,900,900), {})]) # 0.81 ratio
    assert len(check_giant_boxes(t_invalid, config)) == 1

def test_check_duplicate_boxes():
    config = QualityConfig(duplicate_iou=0.9)
    t_valid = create_task([
        Annotation("1", "x", BoundingBox(0,0,10,10), {}),
        Annotation("2", "x", BoundingBox(20,20,10,10), {})
    ])
    assert not check_duplicate_boxes(t_valid, config)

    t_invalid = create_task([
        Annotation("1", "x", BoundingBox(0,0,10,10), {}),
        Annotation("2", "x", BoundingBox(0,0,10,10), {})
    ])
    assert len(check_duplicate_boxes(t_invalid, config)) == 1

def test_check_suspicious_containment():
    config = QualityConfig(suspicious_containment_ratio=0.9)
    t_valid = create_task([
        Annotation("1", "x", BoundingBox(0,0,10,10), {}),
        Annotation("2", "x", BoundingBox(20,20,10,10), {})
    ])
    assert not check_suspicious_containment(t_valid, config)

    t_invalid = create_task([
        Annotation("inner", "x", BoundingBox(5,5,5,5), {}),
        Annotation("outer", "x", BoundingBox(0,0,20,20), {})
    ])
    assert len(check_suspicious_containment(t_invalid, config)) == 1
