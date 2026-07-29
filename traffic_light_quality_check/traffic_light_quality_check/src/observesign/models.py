from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid

@dataclass
class Annotation:
    uuid: str
    label: str
    geometry: str
    left: float
    top: float
    width: float
    height: float
    attributes: Dict[str, str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        return cls(
            uuid=data.get('uuid', str(uuid.uuid4())),
            label=data.get('label', ''),
            geometry=data.get('geometry', 'box'),
            left=data.get('left', 0.0),
            top=data.get('top', 0.0),
            width=data.get('width', 0.0),
            height=data.get('height', 0.0),
            attributes=data.get('attributes', {})
        )

@dataclass
class Task:
    task_id: str
    annotations: List[Annotation]
    image_width: Optional[float] = None
    image_height: Optional[float] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        task_id = data.get('task_id', '')
        response = data.get('response', {})
        annotations_data = response.get('annotations', [])

        # We might have image width/height in attachment metadata, if not we keep None
        # Geometry rule GEO-001 needs image bounds if available.

        annotations = [Annotation.from_dict(ann) for ann in annotations_data]
        return cls(
            task_id=task_id,
            annotations=annotations,
            raw_data=data
        )

@dataclass
class Finding:
    task_id: str
    rule_id: str
    severity: str
    category: str
    explanation: str
    annotation_id: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "category": self.category,
            "annotation_id": self.annotation_id,
            "explanation": self.explanation,
            "evidence": self.evidence
        }
