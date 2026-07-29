from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class BoundingBox:
    left: float
    top: float
    width: float
    height: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoundingBox':
        return cls(
            left=float(data.get('left', 0)),
            top=float(data.get('top', 0)),
            width=float(data.get('width', 0)),
            height=float(data.get('height', 0))
        )

@dataclass
class Annotation:
    uuid: str
    label: str
    attributes: Dict[str, str]
    geometry: str
    box: BoundingBox

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        return cls(
            uuid=data.get('uuid', ''),
            label=data.get('label', ''),
            attributes=data.get('attributes', {}),
            geometry=data.get('geometry', 'box'),
            box=BoundingBox.from_dict(data)
        )

@dataclass
class Task:
    task_id: str
    annotations: List[Annotation]
    image_width: Optional[float] = None # Some tasks might have this in response or params, will attempt to find or default
    image_height: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        annotations_data = data.get('response', {}).get('annotations', [])
        annotations = [Annotation.from_dict(ann) for ann in annotations_data]
        return cls(
            task_id=data.get('task_id', ''),
            annotations=annotations,
            # If width/height exist in response or params, they could be added here, otherwise we infer later if needed
            # Looking at output.json, there isn't explicit image dimensions for every task.
        )

@dataclass
class Finding:
    task_id: str
    rule_id: str
    severity: str
    category: str
    message: str
    annotation_id: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "category": self.category,
            "annotation_id": self.annotation_id,
            "message": self.message,
            "evidence": self.evidence
        }
