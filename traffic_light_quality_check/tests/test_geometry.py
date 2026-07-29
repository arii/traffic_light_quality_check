from traffic_light.models import BoundingBox
from traffic_light.rules import box_area, box_area_ratio, intersection_area, intersection_over_union, containment_ratio, is_out_of_bounds

def test_box_area():
    box = BoundingBox(0, 0, 10, 10)
    assert box_area(box) == 100

def test_box_area_ratio():
    box = BoundingBox(0, 0, 10, 10)
    assert box_area_ratio(box, 100, 100) == 0.01

def test_intersection_area():
    box1 = BoundingBox(0, 0, 10, 10)
    box2 = BoundingBox(5, 5, 10, 10)
    assert intersection_area(box1, box2) == 25

def test_intersection_over_union():
    box1 = BoundingBox(0, 0, 10, 10)
    box2 = BoundingBox(5, 5, 10, 10)
    assert intersection_over_union(box1, box2) == 25 / (100 + 100 - 25)

def test_intersection_over_union_identical():
    box1 = BoundingBox(0, 0, 10, 10)
    box2 = BoundingBox(0, 0, 10, 10)
    assert intersection_over_union(box1, box2) == 1.0

def test_intersection_over_union_degenerate_boxes():
    # Box with negative size/degenerate dimensions where union could be <= 0.0
    box1 = BoundingBox(0, 0, -10, 10)
    box2 = BoundingBox(0, 0, 10, -10)
    # intersection_over_union should safely return 0.0 and guard against ZeroDivisionError
    assert intersection_over_union(box1, box2) == 0.0

    # Box with zero width/height
    box3 = BoundingBox(0, 0, 0, 0)
    box4 = BoundingBox(0, 0, 0, 0)
    assert intersection_over_union(box3, box4) == 0.0

def test_containment_ratio():
    inner = BoundingBox(2, 2, 5, 5)
    outer = BoundingBox(0, 0, 10, 10)
    assert containment_ratio(inner, outer) == 1.0

def test_is_out_of_bounds():
    box_out_left = BoundingBox(-1, 5, 10, 10)
    box_out_right = BoundingBox(95, 5, 10, 10) # 95 + 10 = 105 > 100
    box_in = BoundingBox(5, 5, 10, 10)

    # Touch boundary cases
    box_touch_left = BoundingBox(0, 5, 10, 10)
    box_touch_top = BoundingBox(5, 0, 10, 10)
    box_touch_right = BoundingBox(90, 5, 10, 10) # 90 + 10 = 100
    box_touch_bottom = BoundingBox(5, 90, 10, 10) # 90 + 10 = 100

    assert is_out_of_bounds(box_out_left, 100, 100) == True
    assert is_out_of_bounds(box_out_right, 100, 100) == True
    assert is_out_of_bounds(box_in, 100, 100) == False

    assert is_out_of_bounds(box_touch_left, 100, 100) == False
    assert is_out_of_bounds(box_touch_top, 100, 100) == False
    assert is_out_of_bounds(box_touch_right, 100, 100) == False
    assert is_out_of_bounds(box_touch_bottom, 100, 100) == False
