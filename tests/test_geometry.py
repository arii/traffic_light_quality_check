from src.observesign.models import BoundingBox
from src.observesign.geometry import (
    box_area,
    box_area_ratio,
    intersection_area,
    intersection_over_union,
    containment_ratio
)

def test_box_area():
    box = BoundingBox(left=0, top=0, width=10, height=20)
    assert box_area(box) == 200.0

def test_box_area_zero():
    box = BoundingBox(left=0, top=0, width=-10, height=20)
    assert box_area(box) == 0.0

def test_box_area_ratio():
    box = BoundingBox(left=0, top=0, width=100, height=100)
    assert box_area_ratio(box, 1000, 1000) == 0.01

def test_intersection_area():
    b1 = BoundingBox(left=0, top=0, width=10, height=10)
    b2 = BoundingBox(left=5, top=5, width=10, height=10)
    assert intersection_area(b1, b2) == 25.0

def test_intersection_area_none():
    b1 = BoundingBox(left=0, top=0, width=10, height=10)
    b2 = BoundingBox(left=20, top=20, width=10, height=10)
    assert intersection_area(b1, b2) == 0.0

def test_intersection_over_union():
    b1 = BoundingBox(left=0, top=0, width=10, height=10)
    b2 = BoundingBox(left=5, top=0, width=10, height=10)
    # intersection = 50, union = 100 + 100 - 50 = 150 -> 50 / 150 = 1/3
    iou = intersection_over_union(b1, b2)
    assert abs(iou - 0.3333333) < 1e-5

def test_containment_ratio():
    outer = BoundingBox(left=0, top=0, width=100, height=100)
    inner = BoundingBox(left=10, top=10, width=10, height=10)
    assert containment_ratio(inner, outer) == 1.0

    partial_inner = BoundingBox(left=95, top=95, width=10, height=10)
    assert containment_ratio(partial_inner, outer) == 0.25
