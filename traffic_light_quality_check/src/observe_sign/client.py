import io
import json
import logging
import urllib.request
import urllib.error
import urllib.parse
import os
from typing import List, Dict, Any
from PIL import Image

from .models import Task, Annotation, BoundingBox


def get_image_size(url: str) -> tuple[int, int] | None:
    """Reads only the first 64 KB of an image URL to extract dimensions via Pillow.

    Pre-buffers the response into io.BytesIO so Pillow can seek without
    downloading the full image. Non-HTTP/HTTPS URLs (e.g. scaledata://) are
    skipped immediately without making a network request.
    """
    if not url:
        return None
    # Only attempt publicly-accessible HTTP/HTTPS URLs.
    # Internal Scale URI schemes (e.g. scaledata://) are not reachable.
    if not url.startswith(("http://", "https://")):
        logging.debug(f"Skipping non-HTTP URL for dimension fetch: {url}")
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            # Pre-buffer the first 64 KB — sufficient for any image format header.
            # Without this, Pillow falls back to fp.read() (entire download) when
            # seek() fails on a raw streaming HTTP response.
            header_bytes = io.BytesIO(response.read(65536))
        with Image.open(header_bytes) as img:
            return img.size  # (width, height)
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

    def get_tasks(self, project_id: str = None, file_path: str = None, status: str = "completed") -> List[Dict[str, Any]]:
        """
        Fetches tasks from a file (if file_path is provided) or from Scale API.
        Only tasks matching `status` are returned (default: 'completed').
        Pass status=None to disable filtering.
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
                if status is not None:
                    tasks = [t for t in tasks if t.get("status") == status]
                return tasks
        elif project_id:
             if not self.api_key:
                 raise ValueError("SCALE_API_KEY environment variable or api_key argument is required when fetching by project_id")
             import base64
             auth_str = f"{self.api_key}:"
             b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

             # Scale API accepts 'project' (name) but not hex project_id as a server-side filter.
             # Always add a server-side hint and then apply client-side filtering as a safety net.
             is_hex_id = len(project_id) == 24 and all(c in "0123456789abcdefABCDEF" for c in project_id)
             param_key = "project_id" if is_hex_id else "project"

             all_tasks = []
             next_token = None
             try:
                 while True:
                     url = f"{self.base_url}/tasks?{param_key}={urllib.parse.quote(project_id)}&limit=100"
                     if status is not None:
                         url += f"&status={urllib.parse.quote(status)}"
                     if next_token:
                         url += f"&next_token={urllib.parse.quote(next_token)}"
                     req = urllib.request.Request(url)
                     req.add_header("Authorization", f"Basic {b64_auth}")
                     req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
                     with urllib.request.urlopen(req) as response:
                         data = json.loads(response.read().decode('utf-8'))
                     all_tasks.extend(data.get("docs", []))
                     if data.get("has_more") and data.get("next_token"):
                         next_token = data["next_token"]
                     else:
                         break
             except urllib.error.URLError as e:
                 logging.error(f"Error fetching from Scale API: {e}")

             # Client-side safety filters — ensures correct project and status even if
             # the API server-side filter doesn't honour the hex project_id param.
             all_tasks = [
                 t for t in all_tasks
                 if t.get("projectId") == project_id
                 or t.get("project") == project_id
                 or t.get("project_id") == project_id
             ]
             if status is not None:
                 all_tasks = [t for t in all_tasks if t.get("status") == status]
             return all_tasks
        else:
             return []

