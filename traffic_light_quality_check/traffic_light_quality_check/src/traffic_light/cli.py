import argparse
import sys
import os
from .client import load_tasks_from_file, ScaleClient
from .engine import Engine
from .output import write_findings_json, write_findings_csv

def main():
    parser = argparse.ArgumentParser(description="Traffic Light Quality Check")
    parser.add_argument("--project-id", type=str, help="Scale API Project ID (mocked currently unless --file is used)")
    parser.add_argument("--file", type=str, help="Path to local JSON file containing tasks (e.g. output.json)")
    parser.add_argument("--output", type=str, required=True, help="Path to output file (.json or .csv)")

    args = parser.parse_args()

    tasks = []
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found.", file=sys.stderr)
            sys.exit(1)
        tasks = load_tasks_from_file(args.file)
    elif args.project_id:
        client = ScaleClient()
        try:
            tasks = client.fetch_tasks(args.project_id)
        except Exception as e:
            print(f"Error fetching from API: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Must provide either --project-id or --file", file=sys.stderr)
        sys.exit(1)

    engine = Engine()
    findings = engine.run_all(tasks)

    if args.output.endswith('.csv'):
        write_findings_csv(findings, args.output)
    else:
        write_findings_json(findings, args.output)

    print(f"Generated {len(findings)} findings. Output written to {args.output}")

if __name__ == "__main__":
    main()
