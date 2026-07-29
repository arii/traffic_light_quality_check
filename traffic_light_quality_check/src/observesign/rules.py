from typing import List
from src.observesign.models import Task, Finding, Annotation
import src.observesign.geometry as geom

VALID_LABELS = {
    "traffic_control_sign",
    "construction_sign",
    "information_sign",
    "policy_sign",
    "non_visible_face"
}

VALID_OCCLUSION = {"0%", "25%", "50%", "75%", "100%"}
VALID_TRUNCATION = {"0%", "25%", "50%", "75%", "100%"}
VALID_BACKGROUND_COLOR = {"white", "yellow", "red", "orange", "green", "blue", "other", "not_applicable"}

def check_tax_001(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label not in VALID_LABELS:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-001",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid label '{ann.label}'. Must be one of {VALID_LABELS}.",
                evidence={"label": ann.label},
                annotation_id=ann.id
            ))
    return findings

def check_tax_002(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        attrs = ann.attributes or {}

        occ = attrs.get("occlusion")
        if occ not in VALID_OCCLUSION:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid or missing 'occlusion' attribute '{occ}'.",
                evidence={"occlusion": occ},
                annotation_id=ann.id
            ))

        trunc = attrs.get("truncation")
        if trunc not in VALID_TRUNCATION:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid or missing 'truncation' attribute '{trunc}'.",
                evidence={"truncation": trunc},
                annotation_id=ann.id
            ))

        bg_color = attrs.get("background_color")
        if bg_color not in VALID_BACKGROUND_COLOR:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid or missing 'background_color' attribute '{bg_color}'.",
                evidence={"background_color": bg_color},
                annotation_id=ann.id
            ))
    return findings

def check_tax_003(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label == "non_visible_face":
            bg_color = (ann.attributes or {}).get("background_color")
            if bg_color != "not_applicable":
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="TAX-003",
                    severity="error",
                    category="taxonomy",
                    explanation=f"Label 'non_visible_face' requires background_color 'not_applicable'. Found '{bg_color}'.",
                    evidence={"background_color": bg_color, "label": ann.label},
                    annotation_id=ann.id
                ))
    return findings

def check_tax_004(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label == "traffic_control_sign":
            is_traffic_light = False
            for k, v in (ann.attributes or {}).items():
                if isinstance(v, str) and "traffic light" in v.lower():
                    is_traffic_light = True

            bg_color = (ann.attributes or {}).get("background_color")
            if is_traffic_light and bg_color != "other":
                 findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="TAX-004",
                    severity="error",
                    category="taxonomy",
                    explanation=f"Traffic lights should have background_color 'other'. Found '{bg_color}'.",
                    evidence={"background_color": bg_color, "label": ann.label},
                    annotation_id=ann.id
                ))
    return findings

def check_geo_001(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if geom.is_out_of_bounds(ann.bounding_box, task.image.width, task.image.height):
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-001",
                severity="error",
                category="geometry",
                explanation="Bounding box exceeds image boundaries or has invalid dimensions.",
                evidence={"box": ann.bounding_box.__dict__, "image_width": task.image.width, "image_height": task.image.height},
                annotation_id=ann.id
            ))
    return findings

def check_geo_002(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if geom.is_micro_box(ann.bounding_box):
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-002",
                severity="warning",
                category="geometry",
                explanation="Bounding box is too small (width/height < 2 or area < 10).",
                evidence={"box": ann.bounding_box.__dict__},
                annotation_id=ann.id
            ))
    return findings

def check_geo_003(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if geom.is_giant_box(ann.bounding_box, task.image.width, task.image.height):
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-003",
                severity="warning",
                category="geometry",
                explanation="Bounding box is unusually large (> 80% of image area).",
                evidence={"box": ann.bounding_box.__dict__, "image_width": task.image.width, "image_height": task.image.height},
                annotation_id=ann.id
            ))
    return findings

def check_ovl_001(task: Task) -> List[Finding]:
    findings = []
    num_anns = len(task.annotations)
    for i in range(num_anns):
        for j in range(i + 1, num_anns):
            ann1 = task.annotations[i]
            ann2 = task.annotations[j]
            iou_val = geom.iou(ann1.bounding_box, ann2.bounding_box)
            if iou_val > 0.90:
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="OVL-001",
                    severity="error",
                    category="overlap",
                    explanation=f"Duplicate or highly overlapping boxes (IoU {iou_val:.2f} > 0.90).",
                    evidence={"iou": iou_val, "annotation_1": ann1.id, "annotation_2": ann2.id},
                    annotation_id=ann1.id
                ))
    return findings

def check_ovl_002(task: Task) -> List[Finding]:
    findings = []
    num_anns = len(task.annotations)
    for i in range(num_anns):
        for j in range(i + 1, num_anns):
            ann1 = task.annotations[i]
            ann2 = task.annotations[j]
            if geom.is_fully_contained(ann1.bounding_box, ann2.bounding_box):
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="OVL-002",
                    severity="warning",
                    category="overlap",
                    explanation=f"Suspicious containment between boxes.",
                    evidence={"annotation_1": ann1.id, "annotation_2": ann2.id},
                    annotation_id=ann1.id
                ))
    return findings

ALL_RULES = [
    check_tax_001,
    check_tax_002,
    check_tax_003,
    check_tax_004,
    check_geo_001,
    check_geo_002,
    check_geo_003,
    check_ovl_001,
    check_ovl_002
]
