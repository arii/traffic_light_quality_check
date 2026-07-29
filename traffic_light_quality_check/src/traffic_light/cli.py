import argparse
import logging
import sys
from typing import List

from .client import ScaleClient, normalize_task
from .engine import audit_tasks
from .rules import QualityConfig
from .output import write_json, write_csv

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description="Automated quality checks for Traffic Sign annotations")
    parser.add_argument("--project-id", type=str, help="Scale API project ID")
    parser.add_argument("--file", type=str, help="Path to local JSON file with task data")
    parser.add_argument("--output", type=str, required=True, help="Path to output file (JSON or CSV)")

    args = parser.parse_args()

    if not args.project_id and not args.file:
        logging.error("Error: Must provide either --project-id or --file")
        sys.exit(1)

    client = ScaleClient()
    raw_tasks = client.get_tasks(project_id=args.project_id, file_path=args.file)

    if not raw_tasks:
        logging.info("No tasks found.")
        sys.exit(1)

    tasks = (normalize_task(t) for t in raw_tasks)

    config = QualityConfig()
    results_by_task = audit_tasks(tasks, config)

    # Flatten findings
    all_findings = [f for task_findings in results_by_task.values() for f in task_findings]

    if args.output.lower().endswith(".csv"):
        write_csv(all_findings, args.output)
    else:
        write_json(all_findings, args.output)

    logging.info(f"Audit complete. Found {len(all_findings)} issues across {len(raw_tasks)} tasks.")
    logging.info(f"Results written to {args.output}")

if __name__ == "__main__":
    main()
