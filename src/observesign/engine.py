from .models import Task, Finding
from .rules import (
    QualityConfig,
    check_invalid_attributes,
    check_background_color,
    check_out_of_bounds,
    check_micro_boxes,
    check_giant_boxes,
    check_duplicate_boxes,
    check_suspicious_containment
)

RULES = [
    check_invalid_attributes,
    check_background_color,
    check_out_of_bounds,
    check_micro_boxes,
    check_giant_boxes,
    check_duplicate_boxes,
    check_suspicious_containment
]

def audit_task(task: Task, config: QualityConfig = None) -> list[Finding]:
    if config is None:
        config = QualityConfig()
    findings = []
    for rule in RULES:
        findings.extend(rule(task, config))
    return findings

def audit_tasks(tasks: list[Task], config: QualityConfig = None) -> dict[str, list[Finding]]:
    return {
        task.id: audit_task(task, config)
        for task in tasks
    }
