import json
import csv
from typing import List, Dict, Any
from src.observesign.models import Finding
from dataclasses import asdict

def export_json(findings: List[Finding], filepath: str) -> None:
    findings_dict = [asdict(f) for f in findings]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(findings_dict, f, indent=2)

def export_csv(findings: List[Finding], filepath: str) -> None:
    if not findings:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            pass
        return

    fields = ['task_id', 'rule_id', 'severity', 'category', 'annotation_id', 'explanation', 'evidence']
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for finding in findings:
            row = asdict(finding)
            # Serialize evidence to JSON string for CSV
            row['evidence'] = json.dumps(row['evidence'])
            writer.writerow(row)

def export_findings(findings: List[Finding], filepath: str) -> None:
    if filepath.endswith('.json'):
        export_json(findings, filepath)
    elif filepath.endswith('.csv'):
        export_csv(findings, filepath)
    else:
        # Default to JSON if unknown
        export_json(findings, filepath)
