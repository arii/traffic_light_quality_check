"""
Output utilities for writing finding reports to JSON and CSV.
"""
import json
import csv
from typing import List
from .models import Finding

def write_findings_json(findings: List[Finding], file_path: str) -> None:
    """Writes findings to a JSON file."""
    data = [f.to_dict() for f in findings]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def write_findings_csv(findings: List[Finding], file_path: str) -> None:
    """Writes findings to a CSV file."""
    if not findings:
        # Create empty file
        with open(file_path, 'w', encoding='utf-8'):
            pass
        return

    fieldnames = ["task_id", "rule_id", "severity", "category", "annotation_id", "explanation", "evidence"]

    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            row = finding.to_dict()
            # Evidence is a dict, we serialize it to json string for csv
            # We prefix string values that start with a formula character to avoid CSV injection.
            task_id = str(row['task_id'])
            if task_id.startswith(('=', '+', '-', '@')):
                row['task_id'] = f"'{task_id}"

            # Only serialize evidence.
            row['evidence'] = json.dumps(row['evidence'])
            writer.writerow(row)
