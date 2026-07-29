import pytest
from src.observesign.models import Task, TaskImage, Annotation, BoundingBox
from src.observesign.engine import run_quality_checks, run_quality_checks_on_tasks

def create_task():
    return Task(
        task_id="task_001",
        image=TaskImage(width=1000, height=1000),
        annotations=[
            Annotation(
                id="ann1",
                label="invalid_label", # TAX-001
                attributes={"occlusion": "0%", "truncation": "0%", "background_color": "not_applicable"},
                bounding_box=BoundingBox(10, 10, 100, 100)
            ),
            Annotation(
                id="ann2",
                label="non_visible_face",
                attributes={"occlusion": "0%", "truncation": "0%", "background_color": "red"}, # TAX-003
                bounding_box=BoundingBox(50, 50, 1, 1) # GEO-002
            )
        ]
    )

def test_run_quality_checks():
    task = create_task()
    findings = run_quality_checks(task)

    # We should have:
    # 1. TAX-001 on ann1
    # 2. TAX-003 on ann2
    # 3. GEO-002 on ann2

    rule_ids = [f.rule_id for f in findings]
    assert "TAX-001" in rule_ids
    assert "TAX-003" in rule_ids
    assert "GEO-002" in rule_ids

def test_run_quality_checks_on_tasks():
    task1 = create_task()
    task2 = Task(
        task_id="task_002",
        image=TaskImage(width=100, height=100),
        annotations=[]
    )

    findings = run_quality_checks_on_tasks([task1, task2])
    assert len(findings) >= 3
    assert all(f.task_id == "task_001" for f in findings)
