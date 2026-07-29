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

def escape_for_html(data: dict | list) -> str:
    """Safely escapes JSON data for embedding in HTML to prevent XSS."""
    json_str = json.dumps(data, ensure_ascii=False)
    # Manual string replacements as fallback/simplified way requested in audit
    return json_str.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
