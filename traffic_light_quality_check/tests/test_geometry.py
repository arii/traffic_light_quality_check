import pytest
from src.observesign.models import BoundingBox
from src.observesign.geometry import area, is_out_of_bounds, is_micro_box, is_giant_box, iou, is_fully_contained

def test_area():
    box = BoundingBox(left=0, top=0, width=10, height=20)
    assert area(box) == 200

    # Negative dimensions
    box2 = BoundingBox(left=0, top=0, width=-5, height=10)
    assert area(box2) == 0

def test_is_out_of_bounds():
    w, h = 100, 100

    # Valid
    box1 = BoundingBox(10, 10, 50, 50)
    assert not is_out_of_bounds(box1, w, h)

    # Out of bounds left
    box2 = BoundingBox(-10, 10, 50, 50)
    assert is_out_of_bounds(box2, w, h)

    # Exceeds width
    box3 = BoundingBox(90, 10, 20, 20)
    assert is_out_of_bounds(box3, w, h)

def test_is_micro_box():
    # Valid
    assert not is_micro_box(BoundingBox(10, 10, 10, 10))

    # Width < 2
    assert is_micro_box(BoundingBox(10, 10, 1, 10))

    # Area < 10 (3 * 3 = 9)
    assert is_micro_box(BoundingBox(10, 10, 3, 3))

def test_is_giant_box():
    w, h = 100, 100  # Area = 10000

    # Valid (5000 < 8000)
    assert not is_giant_box(BoundingBox(0, 0, 100, 50), w, h)

    # Giant (> 8000)
    assert is_giant_box(BoundingBox(0, 0, 100, 81), w, h)

def test_iou():
    box1 = BoundingBox(0, 0, 10, 10)
    box2 = BoundingBox(0, 0, 10, 10)
    assert iou(box1, box2) == 1.0

    box3 = BoundingBox(10, 10, 10, 10)
    assert iou(box1, box3) == 0.0

    box4 = BoundingBox(5, 0, 10, 10)
    assert iou(box1, box4) == 50 / (100 + 100 - 50) # 50 / 150 = 1/3

def test_is_fully_contained():
    box_large = BoundingBox(0, 0, 100, 100)
    box_small = BoundingBox(10, 10, 50, 50)

    assert is_fully_contained(box_large, box_small)
    assert is_fully_contained(box_small, box_large)

    box_outside = BoundingBox(110, 110, 10, 10)
    assert not is_fully_contained(box_large, box_outside)
