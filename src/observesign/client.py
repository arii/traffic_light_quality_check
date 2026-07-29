import requests
from typing import Dict, Any, List
from .models import Task, Annotation, BoundingBox

class ScaleClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.scale.com/v1"

    def get_tasks(self, project_id: str, status: str = "completed", limit: int = 100) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/tasks"
        params = {
            "project_id": project_id,
            "status": status,
            "limit": limit
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("docs", [])


def normalize_task(raw: Dict[str, Any]) -> Task:
    task_id = raw.get("task_id", "")
    params = raw.get("params", {})
    image_url = params.get("attachment", "")

    # Normally Scale includes image dimensions in metadata or params
    # We will look for it but NOT artificially expand it when boxes are out of bounds,
    # because that would defeat the out-of-bounds rule.
    # Fallback to a fixed size only if we can't get it from API response,
    # but for typical Scale CV tasks, it's often in metadata.
    image_width = raw.get("metadata", {}).get("image_width", 1920)
    image_height = raw.get("metadata", {}).get("image_height", 1080)

    if "image_width" in params:
        image_width = params["image_width"]
    if "image_height" in params:
        image_height = params["image_height"]

    annotations_data = raw.get("response", {}).get("annotations", [])
    annotations = []

    for ann in annotations_data:
        box = BoundingBox(
            left=float(ann.get("left", 0)),
            top=float(ann.get("top", 0)),
            width=float(ann.get("width", 0)),
            height=float(ann.get("height", 0))
        )
        attributes = ann.get("attributes", {})

        annotation = Annotation(
            id=ann.get("uuid", ""),
            label=ann.get("label", ""),
            box=box,
            attributes=attributes
        )
        annotations.append(annotation)

    return Task(
        id=task_id,
        image_url=image_url,
        image_width=image_width,
        image_height=image_height,
        annotations=annotations
    )
