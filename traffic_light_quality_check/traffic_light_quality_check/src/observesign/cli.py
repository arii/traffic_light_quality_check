"""
Command line interface for ObserveSign quality check tool.
"""
import argparse
import json
from dotenv import load_dotenv
from .client import ScaleClient
from .engine import QualityEngine
from .output import write_findings_json, write_findings_csv

def main():
    """Main CLI entrypoint."""
    load_dotenv()

    parser = argparse.ArgumentParser(description="ObserveSign Quality Checker")
    parser.add_argument("--project-id", type=str, help="Scale API project ID")
    parser.add_argument("--input", type=str, help="Path to local JSON input (for testing without API)")
    parser.add_argument("--output", type=str, required=True, help="Path to output file (.json or .csv)")
    parser.add_argument("--limit", type=int, default=100, help="Limit number of tasks fetched")

    args = parser.parse_args()

    if not args.project_id and not args.input:
        parser.error("Either --project-id or --input must be provided.")

    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
            # If the file contains a dict with 'docs' key (Scale API standard response structure)
            if isinstance(tasks_data, dict) and 'docs' in tasks_data:
                tasks_data = tasks_data['docs']
    else:
        client = ScaleClient()
        tasks_data = client.get_tasks(project_id=args.project_id, limit=args.limit)

    engine = QualityEngine()
    findings = engine.evaluate_tasks_from_dicts(tasks_data)

    if args.output.endswith('.json'):
        write_findings_json(findings, args.output)
    elif args.output.endswith('.csv'):
        write_findings_csv(findings, args.output)
    else:
        parser.error("Output file must end with .json or .csv")

    print(f"Generated {len(findings)} findings in {args.output}")

if __name__ == "__main__":
    main()
