from typing import Tuple
from .models import Annotation

def get_bounds(ann: Annotation) -> Tuple[float, float, float, float]:
    """Returns (x_min, y_min, x_max, y_max)"""
    return (ann.left, ann.top, ann.left + ann.width, ann.top + ann.height)

def area(ann: Annotation) -> float:
    return ann.width * ann.height

def intersection_area(ann1: Annotation, ann2: Annotation) -> float:
    x_min1, y_min1, x_max1, y_max1 = get_bounds(ann1)
    x_min2, y_min2, x_max2, y_max2 = get_bounds(ann2)

    inter_x_min = max(x_min1, x_min2)
    inter_y_min = max(y_min1, y_min2)
    inter_x_max = min(x_max1, x_max2)
    inter_y_max = min(y_max1, y_max2)

    if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
        return 0.0

    return (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)

def calculate_iou(ann1: Annotation, ann2: Annotation) -> float:
    inter = intersection_area(ann1, ann2)
    if inter == 0:
        return 0.0

    a1 = area(ann1)
    a2 = area(ann2)

    union = a1 + a2 - inter
    if union <= 0:
        return 0.0

    return inter / union

def is_fully_contained(ann1: Annotation, ann2: Annotation) -> bool:
    """Returns True if ann1 is fully contained within ann2."""
    x_min1, y_min1, x_max1, y_max1 = get_bounds(ann1)
    x_min2, y_min2, x_max2, y_max2 = get_bounds(ann2)

    return (x_min1 >= x_min2 and
            y_min1 >= y_min2 and
            x_max1 <= x_max2 and
            y_max1 <= y_max2)
