import unittest
from traffic_light.models import BoundingBox
from traffic_light import geometry

class TestGeometry(unittest.TestCase):
    def test_area(self):
        box = BoundingBox(left=0, top=0, width=10, height=10)
        self.assertEqual(geometry.area(box), 100)

    def test_intersection_and_iou(self):
        box1 = BoundingBox(left=0, top=0, width=10, height=10)
        box2 = BoundingBox(left=5, top=5, width=10, height=10)

        # Intersect area: left=5, top=5, right=10, bottom=10 -> width=5, height=5 -> 25
        self.assertEqual(geometry.intersection(box1, box2), 25)

        # IoU: 25 / (100 + 100 - 25) = 25 / 175 = 1/7
        self.assertAlmostEqual(geometry.iou(box1, box2), 1/7)

    def test_containment(self):
        outer = BoundingBox(left=0, top=0, width=20, height=20)
        inner = BoundingBox(left=5, top=5, width=10, height=10)

        self.assertTrue(geometry.is_fully_contained(inner, outer))
        self.assertFalse(geometry.is_fully_contained(outer, inner))

if __name__ == '__main__':
    unittest.main()
