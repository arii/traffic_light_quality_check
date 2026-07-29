import json
import urllib.request
import urllib.error
import urllib.parse
import os
from typing import List, Dict, Any

from .models import Task, Annotation, BoundingBox

def normalize_task(raw_task: Dict[str, Any]) -> Task:
    """Converts a raw Scale API task dictionary into the internal Task model."""
    task_id = raw_task.get("task_id", raw_task.get("_id", "unknown"))

    image_url = ""
    params = raw_task.get("params", {})
    if "attachment" in params:
         image_url = params["attachment"]

    # Often, image dimensions aren't provided in the scale API directly in the root,
    # let's assume default large size for safety if not present, or try to infer.
    # In some real-world data, they are provided inside params or metadata.
    # We will set a default large dimension to prevent division by zero, and allow out-of-bounds to just test zero bound.
    # For a real integration, we might need to fetch the image and get size.
    image_width = params.get("image_width", 2000)
    image_height = params.get("image_height", 2000)

    annotations = []

    response = raw_task.get("response", {})
    raw_annotations = response.get("annotations", [])

    for raw_ann in raw_annotations:
        ann_id = raw_ann.get("uuid", "unknown")
        label = raw_ann.get("label", "unknown")

        # Bounding box
        left = float(raw_ann.get("left", 0.0))
        top = float(raw_ann.get("top", 0.0))
        width = float(raw_ann.get("width", 0.0))
        height = float(raw_ann.get("height", 0.0))
        box = BoundingBox(left=left, top=top, width=width, height=height)

        attributes = raw_ann.get("attributes", {})

        annotations.append(Annotation(
            id=ann_id,
            label=label,
            box=box,
            attributes=attributes
        ))

    return Task(
        id=task_id,
        image_url=image_url,
        image_width=image_width,
        image_height=image_height,
        annotations=annotations
    )

class ScaleClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("SCALE_API_KEY", "")
        self.base_url = "https://api.scale.com/v1"

    def get_tasks(self, project_id: str = None, file_path: str = None) -> List[Dict[str, Any]]:
        """
        Fetches tasks from a file (if file_path is provided) or from Scale API (not fully implemented).
        """
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif "docs" in data:
                    return data["docs"]
                elif "tasks" in data:
                    return data["tasks"]
                return [data]
        elif project_id:
             # Basic implementation that could connect to scale
             import base64
             auth_str = f"{self.api_key}:"
             b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
             url = f"{self.base_url}/tasks?project={urllib.parse.quote(project_id)}"
             req = urllib.request.Request(url, headers={"Authorization": f"Basic {b64_auth}"})
             try:
                 with urllib.request.urlopen(req) as response:
                     data = json.loads(response.read().decode('utf-8'))
                     return data.get("docs", [])
             except urllib.error.URLError as e:
                 print(f"Error fetching from Scale API: {e}")
                 return []
        else:
             return []
