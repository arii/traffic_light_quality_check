from .models import BoundingBox

def box_area(box: BoundingBox) -> float:
    """Returns the area of the bounding box."""
    return box.width * box.height

def box_area_ratio(box: BoundingBox, image_width: int, image_height: int) -> float:
    """Returns the ratio of the box area to the image area."""
    area = box_area(box)
    image_area = image_width * image_height
    if image_area == 0:
        return 0.0
    return area / image_area

def intersection_area(first: BoundingBox, second: BoundingBox) -> float:
    """Returns the intersection area of two bounding boxes."""
    x_left = max(first.left, second.left)
    y_top = max(first.top, second.top)
    x_right = min(first.left + first.width, second.left + second.width)
    y_bottom = min(first.top + first.height, second.top + second.height)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    return (x_right - x_left) * (y_bottom - y_top)

def intersection_over_union(first: BoundingBox, second: BoundingBox) -> float:
    """Returns the Intersection-over-Union (IoU) of two bounding boxes."""
    inter = intersection_area(first, second)
    if inter == 0.0:
        return 0.0

    area_first = box_area(first)
    area_second = box_area(second)

    union = area_first + area_second - inter
    if union == 0.0:
        return 0.0
    return inter / union

def containment_ratio(inner: BoundingBox, outer: BoundingBox) -> float:
    """Returns what portion of the inner box is contained within the outer box."""
    inter = intersection_area(inner, outer)
    area_inner = box_area(inner)
    if area_inner == 0.0:
        return 0.0
    return inter / area_inner

def is_out_of_bounds(box: BoundingBox, image_width: int, image_height: int) -> bool:
    """Returns True if the box is outside or touches the image boundary."""
    if box.left <= 0 or box.top <= 0:
        return True
    if box.left + box.width >= image_width:
        return True
    if box.top + box.height >= image_height:
        return True
    return False

def aspect_ratio(box: BoundingBox) -> float:
    """Returns the aspect ratio (width / height) of the box."""
    if box.height == 0:
        return 0.0
    return box.width / box.height
