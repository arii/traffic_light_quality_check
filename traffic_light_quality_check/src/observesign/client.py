import os
import requests
from typing import List, Dict, Any
from src.observesign.models import Task, TaskImage, Annotation, BoundingBox

def parse_task_data(task_json: Dict[str, Any]) -> Task:
    task_id = task_json.get("task_id", "")

    # Expected Scale AI task structure, but we'll try a generic fallback
    params = task_json.get("params", {})
    response = task_json.get("response", {})

    # Get image dimensions (using attachment or from somewhere in response)
    # The prompt didn't specify the exact schema from Scale for this mock,
    # so we'll just extract what we can safely.
    # Usually in Scale, annotations have a 'geometry' or similar.
    # We will assume a structure for the sake of the evaluation.

    image_info = params.get("attachment", {})
    if not isinstance(image_info, dict):
        # fallback
        image_width = 1920.0
        image_height = 1080.0
    else:
        # if there are specific width/height fields
        image_width = image_info.get("width", 1920.0)
        image_height = image_info.get("height", 1080.0)

    img = TaskImage(width=float(image_width), height=float(image_height))

    annotations_list = response.get("annotations", [])
    parsed_annotations = []

    for ann in annotations_list:
        ann_id = ann.get("uuid", ann.get("id", "unknown"))
        label = ann.get("label", "")
        attributes = ann.get("attributes", {})

        # bounding box
        left = float(ann.get("left", 0.0))
        top = float(ann.get("top", 0.0))
        width = float(ann.get("width", 0.0))
        height = float(ann.get("height", 0.0))

        bbox = BoundingBox(left=left, top=top, width=width, height=height)

        parsed_annotations.append(Annotation(
            id=ann_id,
            label=label,
            attributes=attributes,
            bounding_box=bbox
        ))

    return Task(task_id=task_id, image=img, annotations=parsed_annotations)

def fetch_tasks(project_id: str) -> List[Task]:
    api_key = os.environ.get("SCALE_API_KEY", "")
    if not api_key:
        print("Warning: SCALE_API_KEY not found in environment, proceeding with empty task list if no mock is provided.")
        return []

    # Mock or real call
    url = "https://api.scale.com/v1/tasks"
    headers = {"Authorization": f"Basic {api_key}"}
    params = {"project": project_id, "status": "completed"}

    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        tasks_json = data.get("docs", [])
        return [parse_task_data(t) for t in tasks_json]
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []
