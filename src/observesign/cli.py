import argparse
import json
import sys
import os
from pathlib import Path

from .client import ScaleClient, normalize_task
from .engine import audit_tasks
from .rules import QualityConfig

def main():
    parser = argparse.ArgumentParser(description="ObserveSign Automated Quality Check Engine")
    parser.add_argument("--project-id", type=str, required=True, help="Scale API project ID")
    parser.add_argument("--output", type=str, required=True, help="Path to save the JSON findings")
    # Add input file as a fallback if they want to bypass API (e.g. tests or local data)
    parser.add_argument("--input", type=str, help="Optional: Input file containing raw task data (bypasses Scale API)")

    args = parser.parse_args()

    raw_tasks = []

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file {input_path} does not exist.")
            sys.exit(1)
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        docs = data.get("docs", []) if isinstance(data, dict) else data
        raw_tasks = [doc for doc in docs if doc.get("projectId") == args.project_id]
    else:
        api_key = os.environ.get("SCALE_API_KEY")
        if not api_key:
            print("Error: SCALE_API_KEY environment variable is required when not using --input.")
            sys.exit(1)
        client = ScaleClient(api_key)
        try:
            raw_tasks = client.get_tasks(project_id=args.project_id)
        except Exception as e:
            print(f"Error fetching tasks from Scale API: {e}")
            sys.exit(1)

    if not raw_tasks:
        print(f"No tasks found for project ID {args.project_id}.")
        sys.exit(0)

    print(f"Found {len(raw_tasks)} tasks. Processing...")

    # Normalize tasks
    tasks = [normalize_task(raw) for raw in raw_tasks]

    # Audit tasks
    config = QualityConfig()
    results = audit_tasks(tasks, config)

    # Format output
    output_data = []
    for task_id, findings in results.items():
        if findings:
            output_data.append({
                "task_id": task_id,
                "status": "flagged",
                "summary": {
                    "findings_count": len(findings),
                    "errors": sum(1 for f in findings if f.severity == "error"),
                    "warnings": sum(1 for f in findings if f.severity == "warning")
                },
                "findings": [
                    {
                        "rule_id": f.rule_id,
                        "severity": f.severity,
                        "category": f.category,
                        "annotation_id": f.annotation_id,
                        "message": f.message,
                        "evidence": f.evidence
                    } for f in findings
                ]
            })

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"Audit complete. Findings written to {output_path}")

if __name__ == "__main__":
    main()
