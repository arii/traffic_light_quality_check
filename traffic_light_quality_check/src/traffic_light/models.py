from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class BoundingBox:
    left: float
    top: float
    width: float
    height: float


@dataclass
class Annotation:
    id: str
    label: str
    box: BoundingBox
    attributes: Dict[str, str]


@dataclass
class Task:
    id: str
    image_url: str
    image_width: int
    image_height: int
    annotations: List[Annotation]


@dataclass
class Finding:
    rule_id: str
    severity: str
    category: str
    message: str
    task_id: str
    annotation_id: str | None = None
    evidence: Dict[str, Any] | None = None
