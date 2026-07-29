import json
import csv
from typing import List
from .models import Finding

def write_findings_json(findings: List[Finding], filepath: str):
    data = [f.to_dict() for f in findings]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def write_findings_csv(findings: List[Finding], filepath: str):
    if not findings:
        with open(filepath, 'w', newline='') as f:
            pass
        return

    # Extract field names from the first finding dict
    fieldnames = list(findings[0].to_dict().keys())

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            row = finding.to_dict()
            # Convert evidence to string for CSV
            if row['evidence'] is not None:
                row['evidence'] = json.dumps(row['evidence'])
            writer.writerow(row)
