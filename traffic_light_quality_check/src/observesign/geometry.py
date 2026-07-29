from src.observesign.models import BoundingBox

def area(box: BoundingBox) -> float:
    return max(0, box.width) * max(0, box.height)

def is_out_of_bounds(box: BoundingBox, image_width: float, image_height: float) -> bool:
    if box.left < 0 or box.top < 0:
        return True
    if box.width <= 0 or box.height <= 0:
        return True
    if box.left + box.width > image_width or box.top + box.height > image_height:
        return True
    return False

def is_micro_box(box: BoundingBox) -> bool:
    if box.width < 2 or box.height < 2:
        return True
    if area(box) < 10:
        return True
    return False

def is_giant_box(box: BoundingBox, image_width: float, image_height: float) -> bool:
    img_area = image_width * image_height
    if img_area == 0:
        return False
    return area(box) > 0.8 * img_area

def intersection_area(box1: BoundingBox, box2: BoundingBox) -> float:
    x_left = max(box1.left, box2.left)
    y_top = max(box1.top, box2.top)
    x_right = min(box1.left + box1.width, box2.left + box2.width)
    y_bottom = min(box1.top + box1.height, box2.top + box2.height)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    return (x_right - x_left) * (y_bottom - y_top)

def iou(box1: BoundingBox, box2: BoundingBox) -> float:
    inter_area = intersection_area(box1, box2)
    if inter_area == 0:
        return 0.0

    area1 = area(box1)
    area2 = area(box2)

    return inter_area / (area1 + area2 - inter_area)

def is_fully_contained(box1: BoundingBox, box2: BoundingBox) -> bool:
    """Returns True if box1 is fully contained within box2, or box2 is fully contained within box1"""
    if box1.left >= box2.left and box1.top >= box2.top and \
       box1.left + box1.width <= box2.left + box2.width and \
       box1.top + box1.height <= box2.top + box2.height:
        return True
    if box2.left >= box1.left and box2.top >= box1.top and \
       box2.left + box2.width <= box1.left + box1.width and \
       box2.top + box2.height <= box1.top + box1.height:
        return True
    return False
