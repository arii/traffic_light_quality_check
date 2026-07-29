from dataclasses import dataclass, field
from typing import List, Set, Dict, Iterable

from .models import Task, Finding, Annotation
from . import geometry

@dataclass
class QualityConfig:
    valid_labels: set[str] = field(default_factory=lambda: {
        "traffic_control_sign",
        "construction_sign",
        "information_sign",
        "policy_sign",
        "non_visible_face"
    })
    valid_attributes: set[str] = field(default_factory=lambda: {
        "occlusion",
        "truncation",
        "background_color"
    })
    valid_occlusion: set[str] = field(default_factory=lambda: {"0%", "25%", "50%", "75%", "100%"})
    valid_truncation: set[str] = field(default_factory=lambda: {"0%", "25%", "50%", "75%", "100%"})
    valid_background: set[str] = field(default_factory=lambda: {
        "white", "red", "orange", "yellow", "green", "blue", "other", "not_applicable"
    })

    giant_box_area_ratio: float = 0.80
    micro_box_width: float = 3.0
    micro_box_height: float = 3.0
    micro_box_area: float = 10.0
    duplicate_iou: float = 0.90
    suspicious_containment_ratio: float = 0.95
    extreme_aspect_ratio_max: float = 10.0
    extreme_aspect_ratio_min: float = 0.1

def check_invalid_labels(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        if ann.label not in config.valid_labels:
            findings.append(Finding(
                rule_id="TAX-001",
                severity="error",
                category="taxonomy",
                message=f"Invalid label '{ann.label}'.",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"label": ann.label}
            ))
    return findings

def check_invalid_attributes(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        for attr_key, attr_val in ann.attributes.items():
            if attr_key not in config.valid_attributes:
                findings.append(Finding(
                    rule_id="TAX-002",
                    severity="error",
                    category="taxonomy",
                    message=f"Invalid attribute key '{attr_key}'.",
                    task_id=task.id,
                    annotation_id=ann.id,
                    evidence={"attribute": attr_key}
                ))
            elif attr_key == "occlusion" and attr_val not in config.valid_occlusion:
                findings.append(Finding(
                    rule_id="TAX-002",
                    severity="error",
                    category="taxonomy",
                    message=f"Invalid occlusion value '{attr_val}'.",
                    task_id=task.id,
                    annotation_id=ann.id,
                    evidence={"attribute": attr_key, "value": attr_val}
                ))
            elif attr_key == "truncation" and attr_val not in config.valid_truncation:
                findings.append(Finding(
                    rule_id="TAX-002",
                    severity="error",
                    category="taxonomy",
                    message=f"Invalid truncation value '{attr_val}'.",
                    task_id=task.id,
                    annotation_id=ann.id,
                    evidence={"attribute": attr_key, "value": attr_val}
                ))
            elif attr_key == "background_color" and attr_val not in config.valid_background:
                findings.append(Finding(
                    rule_id="TAX-002",
                    severity="error",
                    category="taxonomy",
                    message=f"Invalid background_color value '{attr_val}'.",
                    task_id=task.id,
                    annotation_id=ann.id,
                    evidence={"attribute": attr_key, "value": attr_val}
                ))
    return findings

def check_out_of_bounds(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    if task.image_width is None or task.image_height is None:
        return findings
    for ann in task.annotations:
        if geometry.is_out_of_bounds(ann.box, task.image_width, task.image_height):
            findings.append(Finding(
                rule_id="GEO-001",
                severity="error",
                category="geometry",
                message="Bounding box is out of image bounds or touches the edges.",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={
                    "box": {"left": ann.box.left, "top": ann.box.top, "width": ann.box.width, "height": ann.box.height},
                    "image_size": {"width": task.image_width, "height": task.image_height}
                }
            ))
    return findings

def check_micro_boxes(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        area = geometry.box_area(ann.box)
        if ann.box.width < config.micro_box_width or \
           ann.box.height < config.micro_box_height or \
           area < config.micro_box_area:
            findings.append(Finding(
                rule_id="GEO-002",
                severity="warning",
                category="geometry",
                message="Bounding box is extremely small.",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"width": ann.box.width, "height": ann.box.height, "area": area}
            ))
    return findings

def check_giant_boxes(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    if task.image_width is None or task.image_height is None:
        return findings
    for ann in task.annotations:
        ratio = geometry.box_area_ratio(ann.box, task.image_width, task.image_height)
        if ratio > config.giant_box_area_ratio:
            findings.append(Finding(
                rule_id="GEO-003",
                severity="warning",
                category="geometry",
                message=f"Bounding box covers {ratio*100:.1f}% of the image.",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"area_ratio": ratio}
            ))
    return findings

def check_extreme_aspect_ratio(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    for ann in task.annotations:
        ratio = geometry.aspect_ratio(ann.box)
        if ratio > config.extreme_aspect_ratio_max or ratio < config.extreme_aspect_ratio_min:
            findings.append(Finding(
                rule_id="GEO-004",
                severity="warning",
                category="geometry",
                message=f"Bounding box has extreme aspect ratio: {ratio:.2f}.",
                task_id=task.id,
                annotation_id=ann.id,
                evidence={"aspect_ratio": ratio}
            ))
    return findings

def check_duplicate_boxes(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    for i in range(len(task.annotations)):
        for j in range(i + 1, len(task.annotations)):
            ann1 = task.annotations[i]
            ann2 = task.annotations[j]
            iou = geometry.intersection_over_union(ann1.box, ann2.box)
            if iou > config.duplicate_iou:
                findings.append(Finding(
                    rule_id="OVL-001",
                    severity="error",
                    category="overlap",
                    message="Annotations are duplicates or near-duplicates.",
                    task_id=task.id,
                    annotation_id=ann1.id,
                    evidence={"iou": iou, "other_annotation_id": ann2.id}
                ))
    return findings

def check_suspicious_containment(task: Task, config: QualityConfig) -> List[Finding]:
    findings = []
    for i in range(len(task.annotations)):
        for j in range(len(task.annotations)):
            if i == j:
                continue
            inner = task.annotations[i]
            outer = task.annotations[j]
            containment = geometry.containment_ratio(inner.box, outer.box)
            # Check if inner is fully contained in outer, but not a duplicate (IoU might be small)
            iou = geometry.intersection_over_union(inner.box, outer.box)
            if containment > config.suspicious_containment_ratio and iou < config.duplicate_iou:
                findings.append(Finding(
                    rule_id="OVL-002",
                    severity="warning",
                    category="overlap",
                    message="Annotation is suspiciously contained within another annotation.",
                    task_id=task.id,
                    annotation_id=inner.id,
                    evidence={"containment_ratio": containment, "outer_annotation_id": outer.id}
                ))
    return findings

RULES = [
    check_invalid_labels,
    check_invalid_attributes,
    check_out_of_bounds,
    check_micro_boxes,
    check_giant_boxes,
    check_extreme_aspect_ratio,
    check_duplicate_boxes,
    check_suspicious_containment,
]

def audit_task(task: Task, config: QualityConfig = None) -> list[Finding]:
    if config is None:
        config = QualityConfig()

    findings = []
    for rule in RULES:
        findings.extend(rule(task, config))

    return findings

def audit_tasks(tasks: Iterable[Task], config: QualityConfig = None) -> dict[str, list[Finding]]:
    return {
        task.id: audit_task(task, config)
        for task in tasks
    }
