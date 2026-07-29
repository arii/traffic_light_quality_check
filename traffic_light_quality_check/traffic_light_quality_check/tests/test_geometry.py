import pytest
from observesign.models import Annotation
from observesign.geometry import intersection_area, calculate_iou, is_fully_contained

def create_ann(left, top, width, height):
    return Annotation(uuid="id", label="label", geometry="box",
                      left=left, top=top, width=width, height=height, attributes={})

def test_iou_non_overlapping():
    a1 = create_ann(0, 0, 10, 10)
    a2 = create_ann(20, 20, 10, 10)
    assert calculate_iou(a1, a2) == 0.0

def test_iou_overlapping():
    a1 = create_ann(0, 0, 10, 10)
    a2 = create_ann(5, 5, 10, 10)
    assert calculate_iou(a1, a2) > 0.0

def test_iou_identical():
    a1 = create_ann(0, 0, 10, 10)
    a2 = create_ann(0, 0, 10, 10)
    assert calculate_iou(a1, a2) == 1.0

def test_is_fully_contained():
    outer = create_ann(0, 0, 100, 100)
    inner = create_ann(10, 10, 50, 50)

    assert is_fully_contained(inner, outer) == True
    assert is_fully_contained(outer, inner) == False

def test_intersection_area():
    a1 = create_ann(0, 0, 10, 10)
    a2 = create_ann(5, 0, 10, 10)
    # intersection should be left=5, top=0, width=5, height=10 => area 50
    assert intersection_area(a1, a2) == 50.0
