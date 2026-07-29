import json
import os
import sys
from typing import Any, List, Dict
from .output import format_findings_as_dicts

def generate_report(tasks: List[Dict[str, Any]], findings: List[Any], output_path: str):
    """Generates the HTML visualization report."""
    template_path = os.path.join(os.path.dirname(__file__), "visualizer_template.html")
    if not os.path.exists(template_path):
        print(f"Error: HTML template not found at {template_path}", file=sys.stderr)
        return

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        tasks_json = json.dumps(tasks, ensure_ascii=False)
        findings_json = json.dumps(format_findings_as_dicts(findings), ensure_ascii=False)

        placeholder = """    // __EMBEDDED_DATA_REPLACEMENT_PLACEHOLDER__
    const EMBEDDED_TASKS = null;
    const EMBEDDED_FINDINGS = null;"""

        replacement = f"""    // __EMBEDDED_DATA_REPLACEMENT_PLACEHOLDER__
    const EMBEDDED_TASKS = {tasks_json};
    const EMBEDDED_FINDINGS = {findings_json};"""

        if placeholder in template_content:
            report_content = template_content.replace(placeholder, replacement)
        else:
            report_content = template_content.replace("const EMBEDDED_TASKS = null;", f"const EMBEDDED_TASKS = {tasks_json};")
            report_content = report_content.replace("const EMBEDDED_FINDINGS = null;", f"const EMBEDDED_FINDINGS = {findings_json};")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"Visualization report generated at {output_path}")
    except Exception as e:
        print(f"Error generating HTML report: {e}", file=sys.stderr)
