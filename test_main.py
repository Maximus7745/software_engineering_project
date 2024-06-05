import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
import main
import tkinter as tk

class TestMain(unittest.TestCase):
    
    def test_create_rounded_rectangle(self):
        # Define the input parameters
        x1, y1, x2, y2, radius = 0, 0, 100, 100, 10
        
        # Call the function
        points = main.create_rounded_rectangle(None, x1, y1, x2, y2, radius)
        
        # Check if the points list has the correct number of coordinates
        self.assertEqual(len(points), 24)
        
        # Check if the points list contains expected coordinates
        expected_points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]
        self.assertEqual(points, expected_points)
    
    @patch('main.tk.Canvas')
    def test_draw_rounded_rectangles(self, mock_canvas):
        # Mock the canvas instances
        left_canvas_instance = Mock()
        right_canvas_instance = Mock()
        mock_canvas.side_effect = [left_canvas_instance, right_canvas_instance]
        
        # Define the global variables for the test
        main.left_canvas = left_canvas_instance
        main.right_canvas = right_canvas_instance
        
        # Define the sizes for the canvas
        left_canvas_instance.winfo_width.return_value = 200
        left_canvas_instance.winfo_height.return_value = 200
        right_canvas_instance.winfo_width.return_value = 200
        right_canvas_instance.winfo_height.return_value = 200
        
        # Call the function
        main.draw_rounded_rectangles()
        
        # Check if the create_polygon method was called for both canvases
        self.assertTrue(left_canvas_instance.create_polygon.called)
        self.assertTrue(right_canvas_instance.create_polygon.called)
        
        # Check the arguments passed to create_polygon
        left_args, left_kwargs = left_canvas_instance.create_polygon.call_args
        right_args, right_kwargs = right_canvas_instance.create_polygon.call_args
        
        self.assertEqual(len(left_args[0]), left_canvas_instance.winfo_width())
        self.assertEqual(len(right_args[0]), right_canvas_instance.winfo_width())

        
if __name__ == '__main__':
    unittest.main()
