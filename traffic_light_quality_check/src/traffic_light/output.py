import json
import csv
from typing import List, Dict

from .models import Finding

def format_findings_as_dicts(findings: List[Finding]) -> List[Dict]:
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
    data = format_findings_as_dicts(findings)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def write_csv(findings: List[Finding], path: str):
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
