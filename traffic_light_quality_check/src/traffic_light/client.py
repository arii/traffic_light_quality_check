import json
import logging
import os
import requests
from typing import List, Dict, Any
from PIL import Image

from .models import Task, Annotation, BoundingBox


def get_image_size(url: str) -> tuple[int, int] | None:
    """Streams only the header bytes necessary to parse image dimensions using Pillow."""
    if not url:
        return None
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, stream=True, timeout=5)
        response.raise_for_status()
        with Image.open(response.raw) as img:
            return img.size  # returns (width, height)
    except Exception as e:
        logging.warning(f"Failed to fetch image dimensions from {url}: {e}")
        return None


def normalize_task(raw_task: Dict[str, Any]) -> Task:
    """Converts a raw Scale API task dictionary into the internal Task model."""
    task_id = raw_task.get("task_id", raw_task.get("_id", "unknown"))

    image_url = ""
    params = raw_task.get("params", {})
    if "attachment" in params:
         image_url = params["attachment"]

    image_width = params.get("image_width")
    image_height = params.get("image_height")

    if (image_width is None or image_height is None) and image_url:
        size = get_image_size(image_url)
        if size:
            image_width, image_height = size

    if image_width is None or image_height is None:
        logging.warning(
            f"Task {task_id} is missing image dimensions. Skipping ratio-based validation checks."
        )

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
        # Try loading .env automatically
        try:
            import dotenv
            dotenv.load_dotenv()
        except ImportError:
            pass
        self.api_key = api_key or os.environ.get("SCALE_API_KEY", "")
        self.base_url = "https://api.scale.com/v1"

    def get_tasks(self, project_id: str = None, file_path: str = None) -> List[Dict[str, Any]]:
        """
        Fetches tasks from a file (if file_path is provided) or from Scale API.
        """
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                tasks = []
                if isinstance(data, list):
                    tasks = data
                elif isinstance(data, dict) and "docs" in data:
                    tasks = data["docs"]
                elif isinstance(data, dict) and "tasks" in data:
                    tasks = data["tasks"]
                else:
                    raise ValueError("Invalid file format. Expected a list of tasks or a dict with 'docs' or 'tasks' keys.")

                if project_id:
                    tasks = [t for t in tasks if t.get("projectId") == project_id or t.get("project") == project_id or t.get("project_id") == project_id]
                return tasks
        elif project_id:
             if not self.api_key:
                 raise ValueError("SCALE_API_KEY environment variable or api_key argument is required when fetching by project_id")

             url = f"{self.base_url}/tasks"
             params = {"project": project_id}
             headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

             try:
                 response = requests.get(
                     url,
                     params=params,
                     headers=headers,
                     auth=(self.api_key, "")
                 )
                 response.raise_for_status()
                 data = response.json()
                 return data.get("docs", [])
             except requests.RequestException as e:
                 logging.error(f"Error fetching from Scale API: {e}")
                 return []
        else:
             return []
