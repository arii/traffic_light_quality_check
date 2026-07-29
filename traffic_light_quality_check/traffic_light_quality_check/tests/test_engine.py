import unittest
from traffic_light.models import Task, Annotation
from traffic_light.engine import Engine
from traffic_light.rules import check_tax_001, check_geo_001

class TestEngine(unittest.TestCase):
    def test_engine_runs_specified_rules(self):
        engine = Engine(rules=[check_tax_001, check_geo_001])
        task = Task(
            task_id="t1",
            annotations=[
                Annotation.from_dict({
                    "uuid": "u1",
                    "label": "invalid_label_here",
                    "left": -10,
                    "top": -10,
                    "width": 50,
                    "height": 50
                })
            ]
        )

        findings = engine.run(task)
        # Should get 1 TAX-001 and 1 GEO-001 finding
        self.assertEqual(len(findings), 2)
        rule_ids = {f.rule_id for f in findings}
        self.assertIn("TAX-001", rule_ids)
        self.assertIn("GEO-001", rule_ids)

if __name__ == '__main__':
    unittest.main()
