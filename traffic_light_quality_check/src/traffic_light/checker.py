from .models import BoundingBox

def box_area(box: BoundingBox) -> float:
    return box.width * box.height

def box_area_ratio(box: BoundingBox, image_width: int, image_height: int) -> float:
    area = box_area(box)
    image_area = image_width * image_height
    if image_area == 0:
        return 0.0
    return area / image_area

def intersection_area(first: BoundingBox, second: BoundingBox) -> float:
    x_left = max(first.left, second.left)
    y_top = max(first.top, second.top)
    x_right = min(first.left + first.width, second.left + second.width)
    y_bottom = min(first.top + first.height, second.top + second.height)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    return (x_right - x_left) * (y_bottom - y_top)

def intersection_over_union(first: BoundingBox, second: BoundingBox) -> float:
    inter = intersection_area(first, second)
    if inter == 0.0:
        return 0.0

    area_first = box_area(first)
    area_second = box_area(second)

    union = area_first + area_second - inter
    if union <= 0.0:
        return 0.0
    return inter / union

def containment_ratio(inner: BoundingBox, outer: BoundingBox) -> float:
    inter = intersection_area(inner, outer)
    area_inner = box_area(inner)
    if area_inner == 0.0:
        return 0.0
    return inter / area_inner

def is_out_of_bounds(box: BoundingBox, image_width: int, image_height: int) -> bool:
    if box.left < 0 or box.top < 0:
        return True
    if box.left + box.width > image_width:
        return True
    if box.top + box.height > image_height:
        return True
    return False

def aspect_ratio(box: BoundingBox) -> float:
    if box.height == 0:
        return 0.0
    return box.width / box.height


from dataclasses import dataclass, field
from typing import List, Set, Dict

from .models import Task, Finding, Annotation


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
        if is_out_of_bounds(ann.box, task.image_width, task.image_height):
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
        area = box_area(ann.box)
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
        ratio = box_area_ratio(ann.box, task.image_width, task.image_height)
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
        ratio = aspect_ratio(ann.box)
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
            iou = intersection_over_union(ann1.box, ann2.box)
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
            containment = containment_ratio(inner.box, outer.box)
            # Check if inner is fully contained in outer, but not a duplicate (IoU might be small)
            iou = intersection_over_union(inner.box, outer.box)
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


from typing import Iterable

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


import json
import csv
from typing import List, Dict

from .models import Finding

def format_findings_as_dicts(findings: List[Finding]) -> List[Dict]:
    """Converts a list of Findings to a list of dicts suitable for JSON."""
    return [
        {
            "task_id": f.task_id,
            "rule_id": f.rule_id,
            "severity": f.severity,
            "category": f.category,
            "annotation_id": f.annotation_id,
            "message": f.message,
            "evidence": f.evidence
        }
        for f in findings
    ]

def write_json(findings: List[Finding], path: str):
    """Writes findings to a JSON file."""
    data = format_findings_as_dicts(findings)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def write_csv(findings: List[Finding], path: str):
    """Writes findings to a CSV file."""
    if not findings:
        # Write empty file if no findings
        with open(path, "w", encoding="utf-8") as f:
            pass
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task_id", "rule_id", "severity", "category", "annotation_id", "message", "evidence"])

        for finding in findings:
            evidence_str = json.dumps(finding.evidence) if finding.evidence else ""
            writer.writerow([
                finding.task_id,
                finding.rule_id,
                finding.severity,
                finding.category,
                finding.annotation_id or "",
                finding.message,
                evidence_str
            ])


import argparse
import logging
import sys
from typing import List

from .client import ScaleClient, normalize_task

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description="Automated quality checks for Traffic Sign annotations")
    parser.add_argument("--project-id", type=str, help="Scale API project ID")
    parser.add_argument("--file", type=str, help="Path to local JSON file with task data")
    parser.add_argument("--output", type=str, required=True, help="Path to output file (JSON or CSV)")
    parser.add_argument("--html", type=str, help="Path to generate interactive HTML visualization report")

    args = parser.parse_args()

    if not args.project_id and not args.file:
        logging.error("Error: Must provide either --project-id or --file")
        sys.exit(1)

    client = ScaleClient()
    raw_tasks = client.get_tasks(project_id=args.project_id, file_path=args.file)

    if not raw_tasks:
        logging.info("No tasks found.")
        sys.exit(1)

    tasks = (normalize_task(t) for t in raw_tasks)

    config = QualityConfig()
    results_by_task = audit_tasks(tasks, config)

    # Flatten findings
    all_findings = [f for task_findings in results_by_task.values() for f in task_findings]

    if args.output.lower().endswith(".csv"):
        write_csv(all_findings, args.output)
    else:
        write_json(all_findings, args.output)

    logging.info(f"Audit complete. Found {len(all_findings)} issues across {len(raw_tasks)} tasks.")
    logging.info(f"Results written to {args.output}")

    if args.html:
        import os
        template_path = os.path.join(os.path.dirname(__file__), "visualizer_template.html")
        if not os.path.exists(template_path):
            print(f"Error: HTML template not found at {template_path}", file=sys.stderr)
        else:
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()

                import json
                tasks_json = json.dumps(raw_tasks, ensure_ascii=False)
                findings_json = json.dumps(format_findings_as_dicts(all_findings), ensure_ascii=False)

                placeholder = """    // __EMBEDDED_DATA_REPLACEMENT_PLACEHOLDER__
    const EMBEDDED_TASKS = null;
    const EMBEDDED_FINDINGS = null;"""

                replacement = f"""    // __EMBEDDED_DATA_REPLACEMENT_PLACEHOLDER__
    const EMBEDDED_TASKS = {tasks_json};
    const EMBEDDED_FINDINGS = {findings_json};"""

                if placeholder in template_content:
                    report_content = template_content.replace(placeholder, replacement)
                else:
                    # Fallback to simple replace
                    report_content = template_content.replace("const EMBEDDED_TASKS = null;", f"const EMBEDDED_TASKS = {tasks_json};")
                    report_content = report_content.replace("const EMBEDDED_FINDINGS = null;", f"const EMBEDDED_FINDINGS = {findings_json};")

                with open(args.html, "w", encoding="utf-8") as f:
                    f.write(report_content)

                print(f"Visualization report generated at {args.html}")
            except Exception as e:
                print(f"Error generating HTML report: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
