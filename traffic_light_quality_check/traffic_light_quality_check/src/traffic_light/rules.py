from typing import List
from .models import Task, Finding, Annotation
from . import geometry

# Expected labels and attributes could ideally be driven by project params, but we encode a default taxonomy based on typical observe sign tasks
EXPECTED_LABELS = {
    "traffic_control_sign", "construction_sign", "information_sign", "policy_sign", "non_visible_face", "traffic_light"
}

def check_tax_001(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label not in EXPECTED_LABELS:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-001",
                severity="error",
                category="taxonomy",
                annotation_id=ann.uuid,
                message=f"Invalid label '{ann.label}' not in expected taxonomy.",
                evidence={"label": ann.label}
            ))
    return findings

def check_tax_002(task: Task) -> List[Finding]:
    findings = []
    # For simplicity, we just check if required attributes exist based on the label, or generic ones
    for ann in task.annotations:
        # Many tasks have occlusion, truncation, background_color
        attrs = ann.attributes
        if "occlusion" not in attrs and "truncation" not in attrs:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-002",
                severity="warning",
                category="taxonomy",
                annotation_id=ann.uuid,
                message="Missing common attributes (occlusion/truncation).",
                evidence={"attributes": attrs}
            ))
    return findings

def check_geo_001(task: Task) -> List[Finding]:
    # Out of bounds check: if coordinates are negative. (We assume image bounds aren't strictly known without image fetch)
    findings = []
    for ann in task.annotations:
        if ann.box.left < 0 or ann.box.top < 0:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-001",
                severity="error",
                category="geometry",
                annotation_id=ann.uuid,
                message="Bounding box is out of bounds (negative coordinates).",
                evidence={"left": ann.box.left, "top": ann.box.top}
            ))
    return findings

def check_geo_002(task: Task) -> List[Finding]:
    # Micro box check
    findings = []
    for ann in task.annotations:
        if ann.box.width < 5 or ann.box.height < 5 or geometry.area(ann.box) < 25:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-002",
                severity="warning",
                category="geometry",
                annotation_id=ann.uuid,
                message="Bounding box is extremely small.",
                evidence={"width": ann.box.width, "height": ann.box.height, "area": geometry.area(ann.box)}
            ))
    return findings

def check_geo_003(task: Task) -> List[Finding]:
    # Giant box check (assuming average large image is say 1920x1080 -> 2M pixels. We use a generic arbitrary threshold if no image size)
    findings = []
    for ann in task.annotations:
        if ann.box.width > 2000 or ann.box.height > 2000 or geometry.area(ann.box) > 1000000:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-003",
                severity="warning",
                category="geometry",
                annotation_id=ann.uuid,
                message="Bounding box is unusually large.",
                evidence={"width": ann.box.width, "height": ann.box.height, "area": geometry.area(ann.box)}
            ))
    return findings

def check_geo_004(task: Task) -> List[Finding]:
    # Extreme aspect ratio
    findings = []
    for ann in task.annotations:
        ar = geometry.aspect_ratio(ann.box)
        if ar < 0.1 or ar > 10.0:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-004",
                severity="warning",
                category="geometry",
                annotation_id=ann.uuid,
                message="Bounding box has an extreme aspect ratio.",
                evidence={"aspect_ratio": ar}
            ))
    return findings

def check_ovl_001(task: Task) -> List[Finding]:
    findings = []
    annotations = task.annotations
    n = len(annotations)
    for i in range(n):
        for j in range(i + 1, n):
            ann1 = annotations[i]
            ann2 = annotations[j]
            iou_val = geometry.iou(ann1.box, ann2.box)
            if iou_val > 0.90:
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="OVL-001",
                    severity="error",
                    category="overlap",
                    annotation_id=ann1.uuid,
                    message="Duplicate or near-duplicate bounding box detected.",
                    evidence={"overlapping_with": ann2.uuid, "iou": iou_val}
                ))
    return findings

def check_ovl_002(task: Task) -> List[Finding]:
    findings = []
    annotations = task.annotations
    n = len(annotations)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            ann1 = annotations[i]
            ann2 = annotations[j]
            # If ann1 is fully inside ann2 and they are of the same class (like traffic sign in traffic sign)
            if geometry.is_fully_contained(ann1.box, ann2.box) and ann1.label == ann2.label:
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="OVL-002",
                    severity="warning",
                    category="overlap",
                    annotation_id=ann1.uuid,
                    message="Suspicious containment: annotation is fully contained within another of the same label.",
                    evidence={"contained_in": ann2.uuid, "label": ann1.label}
                ))
    return findings

ALL_RULES = [
    check_tax_001,
    check_tax_002,
    check_geo_001,
    check_geo_002,
    check_geo_003,
    check_geo_004,
    check_ovl_001,
    check_ovl_002
]
