import os
import json
import tempfile
from unittest.mock import patch
from traffic_light.cli import main

def test_html_report_generation():
    # Setup mock tasks data with an invalid label to trigger a finding
    mock_tasks = [
        {
            "task_id": "test_task_1",
            "project": "ObserveSign",
            "params": {
                "attachment": "https://example.com/image.png",
                "image_width": 1000,
                "image_height": 1000
            },
            "response": {
                "annotations": [
                    {
                        "uuid": "ann_1",
                        "label": "invalid_label",
                        "left": 10,
                        "top": 10,
                        "width": 50,
                        "height": 50,
                        "attributes": {}
                    }
                ]
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save mock tasks to a local file
        input_json_path = os.path.join(tmpdir, "input_tasks.json")
        with open(input_json_path, "w", encoding="utf-8") as f:
            json.dump(mock_tasks, f)

        output_json_path = os.path.join(tmpdir, "output_findings.json")
        output_html_path = os.path.join(tmpdir, "report.html")

        # Mock sys.argv to call cli with HTML output
        test_args = [
            "traffic-light-check",
            "--file", input_json_path,
            "--output", output_json_path,
            "--html", output_html_path
        ]

        with patch("sys.argv", test_args):
            main()

        # Check that output files were generated
        assert os.path.exists(output_json_path)
        assert os.path.exists(output_html_path)

        # Check content of HTML report
        with open(output_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Check that HTML report contains embedded tasks and findings
        assert "test_task_1" in html_content
        assert "TAX-001" in html_content  # Due to "invalid_label"
        assert "EMBEDDED_TASKS =" in html_content
        assert "EMBEDDED_FINDINGS =" in html_content
