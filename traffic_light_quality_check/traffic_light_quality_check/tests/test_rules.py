import unittest
from traffic_light.models import Task, Annotation, BoundingBox
from traffic_light import rules

def create_task(annotations_data):
    return Task(
        task_id="test_task",
        annotations=[
            Annotation.from_dict({
                "uuid": f"uuid_{i}",
                "label": ann.get("label", "traffic_control_sign"),
                "attributes": ann.get("attributes", {"occlusion": "0%", "truncation": "0%"}),
                "geometry": "box",
                "left": ann["box"][0],
                "top": ann["box"][1],
                "width": ann["box"][2],
                "height": ann["box"][3]
            }) for i, ann in enumerate(annotations_data)
        ]
    )

class TestRules(unittest.TestCase):
    def test_tax_001_invalid_label(self):
        task = create_task([
            {"label": "unknown_sign", "box": [0, 0, 10, 10]},
            {"label": "traffic_control_sign", "box": [20, 20, 10, 10]}
        ])
        findings = rules.check_tax_001(task)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].annotation_id, "uuid_0")

    def test_geo_001_out_of_bounds(self):
        task = create_task([
            {"box": [-5, 10, 10, 10]},
            {"box": [10, -5, 10, 10]},
            {"box": [10, 10, 10, 10]}
        ])
        findings = rules.check_geo_001(task)
        self.assertEqual(len(findings), 2)

    def test_ovl_001_duplicate_boxes(self):
        task = create_task([
            {"box": [10, 10, 50, 50]},
            {"box": [11, 11, 48, 48]}, # Highly overlapping
            {"box": [100, 100, 50, 50]}
        ])
        findings = rules.check_ovl_001(task)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].annotation_id, "uuid_0")

    def test_ovl_002_suspicious_containment(self):
        task = create_task([
            {"label": "traffic_control_sign", "box": [10, 10, 100, 100]},
            {"label": "traffic_control_sign", "box": [20, 20, 10, 10]}, # fully contained
            {"label": "policy_sign", "box": [30, 30, 10, 10]} # fully contained but different label
        ])
        findings = rules.check_ovl_002(task)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].annotation_id, "uuid_1")

if __name__ == '__main__':
    unittest.main()
