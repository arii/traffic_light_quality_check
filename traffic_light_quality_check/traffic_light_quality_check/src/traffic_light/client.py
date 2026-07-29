import json
import requests
import os
from typing import List, Dict, Any
from .models import Task

class ScaleClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SCALE_API_KEY", "")
        self.base_url = "https://api.scale.com/v1"

    def fetch_tasks(self, project_id: str) -> List[Task]:
        """Fetches tasks from Scale API."""
        if not self.api_key:
            raise ValueError("SCALE_API_KEY is not set.")

        headers = {"Authorization": f"Basic {self.api_key}"}
        url = f"{self.base_url}/tasks?project_id={project_id}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "docs" in data:
            items = data["docs"]
        elif isinstance(data, list):
            items = data
        else:
            items = [data]

        return [Task.from_dict(item) for item in items]

def load_tasks_from_file(filepath: str) -> List[Task]:
    with open(filepath, 'r') as f:
        data = json.load(f)

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and "docs" in data:
        items = data["docs"]
    else:
        # Attempt to handle generic dict
        items = [data]

    return [Task.from_dict(item) for item in items]
