import argparse
from src.observesign.client import fetch_tasks
from src.observesign.engine import run_quality_checks_on_tasks
from src.observesign.output import export_findings
from dotenv import load_dotenv

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Automated quality checks for ObserveSign annotations")
    parser.add_argument("--project-id", required=True, help="Scale API Project ID")
    parser.add_argument("--output", required=True, help="Output file path (.json or .csv)")

    args = parser.parse_args()

    # 1. Fetch
    tasks = fetch_tasks(args.project_id)
    if not tasks:
        print(f"No tasks found or error fetching tasks for project '{args.project_id}'.")

    # 2. Check
    findings = run_quality_checks_on_tasks(tasks)

    # 3. Export
    export_findings(findings, args.output)
    print(f"Quality checks complete. Wrote {len(findings)} findings to {args.output}")

if __name__ == "__main__":
    main()
