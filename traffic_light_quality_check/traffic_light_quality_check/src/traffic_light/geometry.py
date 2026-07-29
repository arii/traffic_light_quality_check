from .models import BoundingBox
from typing import Tuple

def area(box: BoundingBox) -> float:
    return max(0.0, box.width) * max(0.0, box.height)

def intersection(box1: BoundingBox, box2: BoundingBox) -> float:
    x_left = max(box1.left, box2.left)
    y_top = max(box1.top, box2.top)
    x_right = min(box1.left + box1.width, box2.left + box2.width)
    y_bottom = min(box1.top + box1.height, box2.top + box2.height)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    return (x_right - x_left) * (y_bottom - y_top)

def iou(box1: BoundingBox, box2: BoundingBox) -> float:
    inter_area = intersection(box1, box2)
    if inter_area == 0.0:
        return 0.0
    union_area = area(box1) + area(box2) - inter_area
    if union_area == 0.0:
        return 0.0
    return inter_area / union_area

def containment_ratio(inner: BoundingBox, outer: BoundingBox) -> float:
    """Calculates what fraction of the inner box is contained within the outer box."""
    inter_area = intersection(inner, outer)
    inner_area = area(inner)
    if inner_area == 0.0:
        return 0.0
    return inter_area / inner_area

def is_fully_contained(inner: BoundingBox, outer: BoundingBox) -> bool:
    return containment_ratio(inner, outer) >= 0.99

def aspect_ratio(box: BoundingBox) -> float:
    """Returns width / height. Avoids division by zero."""
    if box.height == 0:
        return float('inf')
    return box.width / box.height
