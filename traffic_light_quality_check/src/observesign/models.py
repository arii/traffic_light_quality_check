from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

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
    attributes: Dict[str, str]
    bounding_box: BoundingBox

@dataclass
class TaskImage:
    width: float
    height: float

@dataclass
class Task:
    task_id: str
    image: TaskImage
    annotations: List[Annotation]

@dataclass
class Finding:
    task_id: str
    rule_id: str
    severity: str
    category: str
    explanation: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    annotation_id: Optional[str] = None
