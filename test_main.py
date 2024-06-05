import pytest
from unittest.mock import MagicMock
from main import create_rounded_rectangle, draw_rounded_rectangles

def test_create_rounded_rectangle():
    canvas = MagicMock()
    result = create_rounded_rectangle(canvas, 0, 0, 100, 100, radius=25)
    expected_points = [25, 0,
                       25, 0,
                       75, 0,
                       75, 0,
                       100, 0,
                       100, 25,
                       100, 25,
                       100, 75,
                       100, 75,
                       100, 100,
                       75, 100,
                       75, 100,
                       25, 100,
                       25, 100,
                       0, 100,
                       0, 75,
                       0, 75,
                       0, 25,
                       0, 25,
                       0, 0]
    assert result == expected_points

def test_draw_rounded_rectangles():
    left_canvas = MagicMock()
    right_canvas = MagicMock()

    left_canvas.winfo_width.return_value = 100
    left_canvas.winfo_height.return_value = 100
    right_canvas.winfo_width.return_value = 200
    right_canvas.winfo_height.return_value = 200

    draw_rounded_rectangles(left_canvas, right_canvas)

    left_canvas.delete.assert_called_once_with("all")
    right_canvas.delete.assert_called_once_with("all")

    left_canvas.create_polygon.assert_called_once()
    right_canvas.create_polygon.assert_called_once()

    left_polygon_args = left_canvas.create_polygon.call_args[0][0]
    right_polygon_args = right_canvas.create_polygon.call_args[0][0]

    assert left_polygon_args == create_rounded_rectangle(left_canvas, 0, 0, 100, 100, radius=25)
    assert right_polygon_args == create_rounded_rectangle(right_canvas, 0, 0, 200, 200, radius=25)
