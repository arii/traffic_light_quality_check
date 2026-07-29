"""
Client for interacting with the Scale API to fetch tasks.
"""
from typing import List, Dict, Any
import os
import requests

class ScaleClient:
    """Client for fetching tasks from the Scale API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("SCALE_API_KEY")
        if not self.api_key:
            raise ValueError("Scale API key is not provided and SCALE_API_KEY is not set.")
        self.base_url = "https://api.scale.com/v1"

    def get_tasks(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetches completed tasks for a specific project from Scale API."""
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

        # Handle pagination for Scale API
        all_tasks = []
        try:
            while url and len(all_tasks) < limit:
                # Add timeout to prevent hanging
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()

                try:
                    data = response.json()
                except ValueError as e:
                    raise ValueError(f"Failed to decode JSON from Scale API: {e}") from e

                # Scale API returns a 'docs' list or directly the list of tasks.
                if "docs" in data:
                    fetched = data["docs"]
                    all_tasks.extend(fetched)

                    if "next_page_token" in data and data["next_page_token"]:
                        params["next_page_token"] = data["next_page_token"]
                    else:
                        break # no more pages
                elif isinstance(data, list):
                    all_tasks.extend(data)
                    break # Not standard pagination format, just break
                else:
                    # Fallback if structure is unknown but similar
                    all_tasks.append(data)
                    break
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error fetching tasks from Scale API: {e}") from e

        return all_tasks[:limit]
