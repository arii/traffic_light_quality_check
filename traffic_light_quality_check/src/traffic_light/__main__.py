import argparse
import logging
import sys
import json
import csv
from typing import List, Dict

from .client import ScaleClient, normalize_task
from .rules import QualityConfig, audit_tasks
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


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description="Automated quality checks for Traffic Sign annotations")
    parser.add_argument("--project-id", type=str, help="Scale API project ID")
    parser.add_argument("--file", type=str, help="Path to local JSON file with task data")
    parser.add_argument("--output", type=str, required=True, help="Path to output file (JSON or CSV)")
    parser.add_argument("--html", type=str, help="Path to generate interactive HTML visualization report")

    args = parser.parse_args()

    if not args.project_id and not args.file:
        logging.error("Error: Must provide either --project-id or --file")
        sys.exit(1)

    client = ScaleClient()
    raw_tasks = client.get_tasks(project_id=args.project_id, file_path=args.file)

    if not raw_tasks:
        logging.info("No tasks found.")
        sys.exit(1)

    tasks = list(normalize_task(t) for t in raw_tasks)

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
        template_path = os.path.join(os.path.dirname(__file__), "visualizer_template.html")
        if not os.path.exists(template_path):
            print(f"Error: HTML template not found at {template_path}", file=sys.stderr)
        else:
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()

                tasks_json = json.dumps(raw_tasks, ensure_ascii=False)
                # "When generating HTML reports (e.g., in `traffic_light/__main__.py`), embedded JSON data must be properly escaped for HTML-sensitive characters to prevent Cross-Site Scripting (XSS) vulnerabilities, as `json.dumps` does not escape characters like `<` or `>` by default."

                tasks_json = tasks_json.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

                findings_dicts = format_findings_as_dicts(all_findings)
                findings_json = json.dumps(findings_dicts, ensure_ascii=False)
                findings_json = findings_json.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

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

                print(f"Visualization report generated at {args.html}")
            except Exception as e:
                print(f"Error generating HTML report: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
