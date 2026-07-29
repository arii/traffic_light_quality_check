"""
Quality check rules for ObserveSign annotations.
"""
from typing import List
from .models import Task, Finding
from .geometry import area, calculate_iou, is_fully_contained

ALLOWED_LABELS = {
    "traffic_control_sign",
    "construction_sign",
    "information_sign",
    "policy_sign",
    "non_visible_face"
}

ALLOWED_OCCLUSION = {"0%", "25%", "50%", "75%", "100%"}
ALLOWED_TRUNCATION = {"0%", "25%", "50%", "75%", "100%"}
ALLOWED_BACKGROUND_COLOR = {"white", "yellow", "red", "orange", "green", "blue", "other", "not_applicable"}

def _check_tax_001(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label not in ALLOWED_LABELS:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-001",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid label '{ann.label}' not in allowed labels.",
                annotation_id=ann.uuid,
                evidence={"label": ann.label}
            ))
    return findings

def _check_tax_002(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        attrs = ann.attributes
        # Missing check
        for req_attr in ["occlusion", "truncation", "background_color"]:
            if req_attr not in attrs:
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="TAX-002",
                    severity="error",
                    category="taxonomy",
                    explanation=f"Missing required attribute '{req_attr}'.",
                    annotation_id=ann.uuid,
                    evidence={"attributes": attrs}
                ))

        # Invalid values check
        if attrs.get("occlusion") and attrs.get("occlusion") not in ALLOWED_OCCLUSION:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid occlusion value '{attrs.get('occlusion')}'.",
                annotation_id=ann.uuid,
                evidence={"occlusion": attrs.get("occlusion")}
            ))
        if attrs.get("truncation") and attrs.get("truncation") not in ALLOWED_TRUNCATION:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid truncation value '{attrs.get('truncation')}'.",
                annotation_id=ann.uuid,
                evidence={"truncation": attrs.get("truncation")}
            ))
        if attrs.get("background_color") and attrs.get("background_color") not in ALLOWED_BACKGROUND_COLOR:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="TAX-002",
                severity="error",
                category="taxonomy",
                explanation=f"Invalid background_color value '{attrs.get('background_color')}'.",
                annotation_id=ann.uuid,
                evidence={"background_color": attrs.get("background_color")}
            ))
    return findings

def _check_tax_003(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label == "non_visible_face":
            bg_color = ann.attributes.get("background_color")
            if bg_color != "not_applicable":
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="TAX-003",
                    severity="error",
                    category="taxonomy",
                    explanation="non_visible_face label must have background_color 'not_applicable'.",
                    annotation_id=ann.uuid,
                    evidence={"label": ann.label, "background_color": bg_color}
                ))
    return findings

def _check_tax_004(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label == "traffic_control_sign":
            is_traffic_light = False

            # 1. From attributes (if the task had a sub-attribute like traffic_light_status)
            if "traffic_light_status" in ann.attributes:
                is_traffic_light = True

            # 2. Heuristic check based on description or if background color was erroneously set to red/yellow/green
            bg = ann.attributes.get("background_color")
            if bg in {"red", "yellow", "green"}:
                is_traffic_light = True

            if is_traffic_light and bg != "other":
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="TAX-004",
                    severity="error",
                    category="taxonomy",
                    explanation="Traffic lights should have background_color 'other'.",
                    annotation_id=ann.uuid,
                    evidence={"label": ann.label, "background_color": bg}
                ))
    return findings

def run_tax_rules(task: Task) -> List[Finding]:
    """Runs all taxonomy rules for a given task."""
    findings = []
    findings.extend(_check_tax_001(task))
    findings.extend(_check_tax_002(task))
    findings.extend(_check_tax_003(task))
    findings.extend(_check_tax_004(task))
    return findings

def _check_geo_001(task: Task) -> List[Finding]:
    findings = []
    img_w = task.image_width
    img_h = task.image_height

    for ann in task.annotations:
        if ann.left < 0 or ann.top < 0 or ann.width < 0 or ann.height < 0:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-001",
                severity="error",
                category="geometry",
                explanation="Bounding box has negative dimensions or coordinates.",
                annotation_id=ann.uuid,
                evidence={"left": ann.left, "top": ann.top, "width": ann.width, "height": ann.height}
            ))
            continue

        if img_w is not None and img_h is not None:
            if (ann.left + ann.width > img_w) or (ann.top + ann.height > img_h):
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="GEO-001",
                    severity="error",
                    category="geometry",
                    explanation="Bounding box exceeds image boundaries.",
                    annotation_id=ann.uuid,
                    evidence={
                        "left": ann.left, "top": ann.top, "width": ann.width, "height": ann.height,
                        "image_width": img_w, "image_height": img_h
                    }
                ))
    return findings

def _check_geo_002(task: Task) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.width < 2 or ann.height < 2 or area(ann) < 10:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-002",
                severity="warning",
                category="geometry",
                explanation="Bounding box is extremely small (micro box).",
                annotation_id=ann.uuid,
                evidence={"width": ann.width, "height": ann.height, "area": area(ann)}
            ))
    return findings

def _check_geo_003(task: Task) -> List[Finding]:
    findings = []
    img_w = task.image_width
    img_h = task.image_height
    img_area = (img_w * img_h) if (img_w and img_h) else None

    for ann in task.annotations:
        a = area(ann)
        if img_area and a > 0.8 * img_area:
            findings.append(Finding(
                task_id=task.task_id,
                rule_id="GEO-003",
                severity="warning",
                category="geometry",
                explanation="Bounding box covers > 80% of the image (giant box).",
                annotation_id=ann.uuid,
                evidence={"box_area": a, "image_area": img_area}
            ))
    return findings

def run_geo_rules(task: Task) -> List[Finding]:
    """Runs all geometric rules for a given task."""
    findings = []
    findings.extend(_check_geo_001(task))
    findings.extend(_check_geo_002(task))
    findings.extend(_check_geo_003(task))
    return findings

def _check_ovl_001(task: Task) -> List[Finding]:
    findings = []
    anns = task.annotations
    n = len(anns)

    for i in range(n):
        for j in range(i + 1, n):
            iou = calculate_iou(anns[i], anns[j])
            if iou > 0.90:
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="OVL-001",
                    severity="error",
                    category="overlap",
                    explanation="Duplicate or highly overlapping boxes (IoU > 0.90).",
                    annotation_id=anns[i].uuid,
                    evidence={"iou": iou, "other_annotation_id": anns[j].uuid}
                ))
    return findings

def _check_ovl_002(task: Task) -> List[Finding]:
    findings = []
    anns = task.annotations
    n = len(anns)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if is_fully_contained(anns[i], anns[j]):
                findings.append(Finding(
                    task_id=task.task_id,
                    rule_id="OVL-002",
                    severity="warning",
                    category="overlap",
                    explanation="Suspicious containment: box is fully contained within another box.",
                    annotation_id=anns[i].uuid,
                    evidence={"contained_in": anns[j].uuid}
                ))
    return findings

def run_ovl_rules(task: Task) -> List[Finding]:
    """Runs all overlap rules for a given task."""
    findings = []
    findings.extend(_check_ovl_001(task))
    findings.extend(_check_ovl_002(task))
    return findings

def run_all_rules(task: Task) -> List[Finding]:
    """Runs all quality rules (taxonomy, geometry, overlap) for a given task."""
    findings = []
    findings.extend(run_tax_rules(task))
    findings.extend(run_geo_rules(task))
    findings.extend(run_ovl_rules(task))
    return findings
