from typing import List, Dict, Any
from .models import Task, Finding
from .rules import run_all_rules

class QualityEngine:
    def __init__(self):
        pass

    def evaluate_task(self, task: Task) -> List[Finding]:
        """Runs all rules on a single task."""
        return run_all_rules(task)

    def evaluate_tasks_from_dicts(self, tasks_data: List[Dict[str, Any]]) -> List[Finding]:
        """Parses raw dicts into Task objects and evaluates them."""
        all_findings = []
        for data in tasks_data:
            task = Task.from_dict(data)

            # Attempt to extract image bounds from params if available
            params = data.get('params', {})
            # There is sometimes a min_width/min_height but we actually need the image dimension.
            # Usually scale API returns 'attachment_width' and 'attachment_height' in response or params.
            # In our data sample, we might not have it.
            # So we check if it exists:
            if 'attachment_width' in params:
                task.image_width = float(params['attachment_width'])
            if 'attachment_height' in params:
                task.image_height = float(params['attachment_height'])

            findings = self.evaluate_task(task)
            all_findings.extend(findings)

        return all_findings
