from .models import BoundingBox

def box_area(box: BoundingBox) -> float:
    return max(0.0, box.width) * max(0.0, box.height)

def box_area_ratio(box: BoundingBox, image_width: int, image_height: int) -> float:
    img_area = float(image_width * image_height)
    if img_area <= 0:
        return 0.0
    return box_area(box) / img_area

def intersection_area(first: BoundingBox, second: BoundingBox) -> float:
    # calculate intersection rectangle
    x_left = max(first.left, second.left)
    y_top = max(first.top, second.top)
    x_right = min(first.left + first.width, second.left + second.width)
    y_bottom = min(first.top + first.height, second.top + second.height)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    return (x_right - x_left) * (y_bottom - y_top)

def intersection_over_union(first: BoundingBox, second: BoundingBox) -> float:
    intersection = intersection_area(first, second)
    area_first = box_area(first)
    area_second = box_area(second)
    union = area_first + area_second - intersection
    if union <= 0:
        return 0.0
    return intersection / union

def containment_ratio(inner: BoundingBox, outer: BoundingBox) -> float:
    # returns the ratio of the intersection area to the area of the inner box
    intersection = intersection_area(inner, outer)
    area_inner = box_area(inner)
    if area_inner <= 0:
        return 0.0
    return intersection / area_inner
