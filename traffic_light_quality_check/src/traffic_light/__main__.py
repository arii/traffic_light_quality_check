import argparse
import logging
import sys

from .client import ScaleClient, normalize_task
from .rules import QualityConfig, audit_tasks
from .output import write_json, write_csv

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description="Automated quality checks for Traffic Sign annotations")
    parser.add_argument("--project-id", type=str, help="Scale API project ID")
    parser.add_argument("--file", type=str, help="Path to local JSON file with task data")
    parser.add_argument("--output", type=str, required=True, help="Path to output file (JSON or CSV)")
    parser.add_argument("--html", type=str, help="Path to generate interactive HTML visualization report")

    args = parser.parse_args()

    if args.project_id and not args.project_id.isalnum():
        raise ValueError("Invalid --project-id format: must be alphanumeric.")

    if not args.project_id and not args.file:
        raise ValueError("Error: Must provide either --project-id or --file")

    client = ScaleClient()
    raw_tasks = client.get_tasks(project_id=args.project_id, file_path=args.file)

    if not raw_tasks:
        logging.info("No tasks found.")
        return

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

    if args.html:
        import os
        from .output import format_findings_as_dicts
        template_path = os.path.join(os.path.dirname(__file__), "visualizer_template.html")
        if not os.path.exists(template_path):
            logging.error(f"Error: HTML template not found at {template_path}")
        else:
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()

                import json
                tasks_json = json.dumps(raw_tasks, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e')
                findings_json = json.dumps(format_findings_as_dicts(all_findings), ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e')

                placeholder = """    // __EMBEDDED_DATA_REPLACEMENT_PLACEHOLDER__
    const EMBEDDED_TASKS = null;
    const EMBEDDED_FINDINGS = null;"""

                replacement = f"""    // __EMBEDDED_DATA_REPLACEMENT_PLACEHOLDER__
    const EMBEDDED_TASKS = {tasks_json};
    const EMBEDDED_FINDINGS = {findings_json};"""

                if placeholder in template_content:
                    report_content = template_content.replace(placeholder, replacement)
                else:
                    # Fallback to simple replace
                    report_content = template_content.replace("const EMBEDDED_TASKS = null;", f"const EMBEDDED_TASKS = {tasks_json};")
                    report_content = report_content.replace("const EMBEDDED_FINDINGS = null;", f"const EMBEDDED_FINDINGS = {findings_json};")

                with open(args.html, "w", encoding="utf-8") as f:
                    f.write(report_content)

                logging.info(f"Visualization report generated at {args.html}")
            except (IOError, OSError) as e:
                logging.exception(f"Error generating HTML report: {e}")

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        logging.error(str(e))
        sys.exit(1)
