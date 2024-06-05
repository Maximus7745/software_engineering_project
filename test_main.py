from unittest.mock import MagicMock
from main import create_rounded_rectangle


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
