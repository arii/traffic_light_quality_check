from typing import List, Dict

from .models import Task, Finding
from .rules import QualityConfig, RULES

def audit_task(task: Task, config: QualityConfig = None) -> List[Finding]:
    """Runs all rules on a single task and returns findings."""
    if config is None:
        config = QualityConfig()

    findings = []
    for rule in RULES:
        findings.extend(rule(task, config))

    return findings

def audit_tasks(tasks: List[Task], config: QualityConfig = None) -> Dict[str, List[Finding]]:
    """Runs all rules on a list of tasks and groups findings by task_id."""
    return {
        task.id: audit_task(task, config)
        for task in tasks
    }
