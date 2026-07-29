from dataclasses import dataclass
from .models import Task, Finding, Annotation

@dataclass(frozen=True)
class QualityConfig:
    giant_box_area_ratio: float = 0.80
    micro_box_width: float = 3
    micro_box_height: float = 3
    micro_box_area: float = 10
    duplicate_iou: float = 0.90
    suspicious_containment_ratio: float = 0.95

VALID_LABELS = {
    "traffic_control_sign",
    "construction_sign",
    "information_sign",
    "policy_sign",
    "non_visible_face"
}

VALID_OCCLUSIONS = {"0%", "25%", "50%", "75%", "100%"}
VALID_TRUNCATIONS = {"0%", "25%", "50%", "75%", "100%"}
VALID_BACKGROUND_COLORS = {
    "white", "red", "orange", "yellow", "green", "blue", "other", "not_applicable"
}

def check_invalid_attributes(task: Task, config: QualityConfig) -> list[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label not in VALID_LABELS:
            findings.append(Finding(
                rule_id="TAX-001",
                severity="error",
                category="taxonomy",
                message=f"Invalid label: {ann.label}",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"label": ann.label}
            ))

        occlusion = ann.attributes.get("occlusion")
        if occlusion is not None and occlusion not in VALID_OCCLUSIONS:
            findings.append(Finding(
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                message=f"Invalid occlusion value: {occlusion}",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"occlusion": occlusion}
            ))

        truncation = ann.attributes.get("truncation")
        if truncation is not None and truncation not in VALID_TRUNCATIONS:
            findings.append(Finding(
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                message=f"Invalid truncation value: {truncation}",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"truncation": truncation}
            ))

    return findings


def check_background_color(task: Task, config: QualityConfig) -> list[Finding]:
    findings = []
    for ann in task.annotations:
        bg_color = ann.attributes.get("background_color")
        if bg_color:
            if bg_color not in VALID_BACKGROUND_COLORS:
                findings.append(Finding(
                    rule_id="TAX-003",
                    severity="error",
                    category="taxonomy",
                    message=f"Invalid background_color value: {bg_color}",
                    task_id=task.id,
                    annotation_id=ann.id,
                    evidence={"background_color": bg_color}
                ))
            elif bg_color == "not_applicable" and ann.label != "non_visible_face":
                findings.append(Finding(
                    rule_id="TAX-004",
                    severity="error",
                    category="taxonomy",
                    message="background_color 'not_applicable' should only be used for 'non_visible_face'",
                    task_id=task.id,
                    annotation_id=ann.id,
                    evidence={"background_color": bg_color, "label": ann.label}
                ))
    return findings

from .geometry import box_area, box_area_ratio

def check_out_of_bounds(task: Task, config: QualityConfig) -> list[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.box.left < 0 or ann.box.top < 0 or \
           ann.box.left + ann.box.width > task.image_width or \
           ann.box.top + ann.box.height > task.image_height:
            findings.append(Finding(
                rule_id="GEO-001",
                severity="error",
                category="geometry",
                message="Bounding box extends beyond image dimensions",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={
                    "box": {"left": ann.box.left, "top": ann.box.top, "width": ann.box.width, "height": ann.box.height},
                    "image": {"width": task.image_width, "height": task.image_height}
                }
            ))
    return findings

def check_micro_boxes(task: Task, config: QualityConfig) -> list[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.box.width < config.micro_box_width or \
           ann.box.height < config.micro_box_height or \
           box_area(ann.box) < config.micro_box_area:
            findings.append(Finding(
                rule_id="GEO-002",
                severity="warning",
                category="geometry",
                message=f"Micro box detected: width={ann.box.width}, height={ann.box.height}",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"width": ann.box.width, "height": ann.box.height, "area": box_area(ann.box)}
            ))
    return findings

def check_giant_boxes(task: Task, config: QualityConfig) -> list[Finding]:
    findings = []
    for ann in task.annotations:
        ratio = box_area_ratio(ann.box, task.image_width, task.image_height)
        if ratio > config.giant_box_area_ratio:
            findings.append(Finding(
                rule_id="GEO-003",
                severity="warning",
                category="geometry",
                message=f"Giant box detected: covers {ratio*100:.1f}% of image",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"area_ratio": ratio}
            ))
    return findings


from .geometry import intersection_over_union, containment_ratio

def check_duplicate_boxes(task: Task, config: QualityConfig) -> list[Finding]:
    findings = []
    annotations = task.annotations
    n = len(annotations)
    for i in range(n):
        for j in range(i + 1, n):
            ann1 = annotations[i]
            ann2 = annotations[j]
            iou = intersection_over_union(ann1.box, ann2.box)
            if iou > config.duplicate_iou:
                findings.append(Finding(
                    rule_id="OVL-001",
                    severity="error",
                    category="overlap",
                    message=f"Duplicate or near-duplicate boxes detected (IoU {iou:.2f})",
                    task_id=task.id,
                    evidence={"iou": iou, "annotation_ids": [ann1.id, ann2.id]}
                ))
    return findings

def check_suspicious_containment(task: Task, config: QualityConfig) -> list[Finding]:
    findings = []
    annotations = task.annotations
    n = len(annotations)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            inner_ann = annotations[i]
            outer_ann = annotations[j]
            ratio = containment_ratio(inner_ann.box, outer_ann.box)
            if ratio > config.suspicious_containment_ratio:
                findings.append(Finding(
                    rule_id="OVL-002",
                    severity="warning",
                    category="overlap",
                    message=f"Suspicious containment: box heavily contains another",
                    task_id=task.id,
                    evidence={
                        "containment_ratio": ratio,
                        "inner_annotation_id": inner_ann.id,
                        "outer_annotation_id": outer_ann.id
                    }
                ))
    return findings
