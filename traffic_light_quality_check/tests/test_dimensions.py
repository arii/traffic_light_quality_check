import pytest
from unittest.mock import patch, MagicMock
from traffic_light.client import get_image_size, normalize_task
from traffic_light.models import Task, Annotation, BoundingBox
from traffic_light.rules import check_out_of_bounds, check_giant_boxes, QualityConfig

def test_get_image_size_success():
    # Mock urllib.request.urlopen to return an image-like object
    mock_img = MagicMock()
    mock_img.size = (1920, 1080)

    with patch("urllib.request.urlopen") as mock_urlopen, \
         patch("PIL.Image.open") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_img

        size = get_image_size("http://example.com/test.jpg")
        assert size == (1920, 1080)
        mock_urlopen.assert_called_once()

def test_get_image_size_failure():
    with patch("urllib.request.urlopen", side_effect=Exception("Network error")):
        size = get_image_size("http://example.com/test.jpg")
        assert size is None

def test_get_image_size_empty_url():
    size = get_image_size("")
    assert size is None

def test_normalize_task_with_dimensions():
    raw_task = {
        "task_id": "task_1",
        "params": {
            "attachment": "http://example.com/image.jpg",
            "image_width": 1280,
            "image_height": 720
        },
        "response": {"annotations": []}
    }
    task = normalize_task(raw_task)
    assert task.image_width == 1280
    assert task.image_height == 720

def test_normalize_task_without_dimensions_success_fetch():
    raw_task = {
        "task_id": "task_2",
        "params": {
            "attachment": "http://example.com/image.jpg"
        },
        "response": {"annotations": []}
    }
    with patch("traffic_light.client.get_image_size", return_value=(800, 600)) as mock_get_size:
        task = normalize_task(raw_task)
        assert task.image_width == 800
        assert task.image_height == 600
        mock_get_size.assert_called_once_with("http://example.com/image.jpg")

def test_normalize_task_without_dimensions_failed_fetch():
    raw_task = {
        "task_id": "task_3",
        "params": {
            "attachment": "http://example.com/image.jpg"
        },
        "response": {"annotations": []}
    }
    with patch("traffic_light.client.get_image_size", return_value=None) as mock_get_size:
        task = normalize_task(raw_task)
        assert task.image_width is None
        assert task.image_height is None
        mock_get_size.assert_called_once_with("http://example.com/image.jpg")

def test_rules_skipped_when_dimensions_none():
    ann = Annotation(
        id="ann_1",
        label="traffic_control_sign",
        box=BoundingBox(left=10, top=10, width=500, height=500),
        attributes={}
    )
    # Task with image dimensions = None
    task = Task(
        id="task_none",
        image_url="http://example.com/image.jpg",
        image_width=None,
        image_height=None,
        annotations=[ann]
    )
    config = QualityConfig()

    # Normally check_out_of_bounds or check_giant_boxes would run.
    # But since dimensions are None, they should be skipped (return no findings).
    out_of_bounds_findings = check_out_of_bounds(task, config)
    assert len(out_of_bounds_findings) == 0

    giant_findings = check_giant_boxes(task, config)
    assert len(giant_findings) == 0
