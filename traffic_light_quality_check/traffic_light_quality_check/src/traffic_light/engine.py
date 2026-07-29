from typing import List, Callable
from .models import Task, Finding
from .rules import ALL_RULES

class Engine:
    def __init__(self, rules: List[Callable[[Task], List[Finding]]] = None):
        self.rules = rules if rules is not None else ALL_RULES

    def run(self, task: Task) -> List[Finding]:
        findings = []
        for rule in self.rules:
            findings.extend(rule(task))
        return findings

    def run_all(self, tasks: List[Task]) -> List[Finding]:
        findings = []
        for task in tasks:
            findings.extend(self.run(task))
        return findings
