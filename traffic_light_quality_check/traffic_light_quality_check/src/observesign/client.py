import os
import requests
from typing import List, Dict, Any

class ScaleClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("SCALE_API_KEY")
        if not self.api_key:
            raise ValueError("Scale API key is not provided and SCALE_API_KEY is not set.")
        self.base_url = "https://api.scale.com/v1"

    def get_tasks(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/tasks"
        params = {
            "project_id": project_id,
            "status": "completed",
            "limit": str(limit)
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Scale API returns a 'docs' list or directly the list of tasks.
        if "docs" in data:
            return data["docs"]
        elif isinstance(data, list):
            return data
        else:
            # Fallback if structure is unknown but similar
            return [data]
