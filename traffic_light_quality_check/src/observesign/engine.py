from typing import List
from src.observesign.models import Task, Finding
from src.observesign.rules import ALL_RULES

def run_quality_checks(task: Task) -> List[Finding]:
    """Run all quality checks on a single task and return a list of findings."""
    all_findings = []
    for rule in ALL_RULES:
        findings = rule(task)
        if findings:
            all_findings.extend(findings)
    return all_findings

def run_quality_checks_on_tasks(tasks: List[Task]) -> List[Finding]:
    """Run quality checks on multiple tasks."""
    all_findings = []
    for task in tasks:
        all_findings.extend(run_quality_checks(task))
    return all_findings
