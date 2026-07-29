from typing import Iterable

from .models import Task, Finding
from .rules import QualityConfig, RULES

def audit_task(task: Task, config: QualityConfig = None) -> list[Finding]:
    """Runs all rules on a single task and returns findings."""
    if config is None:
        config = QualityConfig()

    findings = []
    for rule in RULES:
        findings.extend(rule(task, config))

    return findings

def audit_tasks(tasks: Iterable[Task], config: QualityConfig = None) -> dict[str, list[Finding]]:
    """Runs all rules on a list of tasks and groups findings by task_id."""
    return {
        task.id: audit_task(task, config)
        for task in tasks
    }
