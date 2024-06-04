import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import main
import tkinter as tk

class TestMain(unittest.TestCase):
    
    @patch('main.build')
    @patch('main.pickle.load')
    @patch('main.pickle.dump')
    @patch('main.os.path.exists')
    def test_get_gmail_messages(self, mock_exists, mock_pickle_load, mock_pickle_dump, mock_build):
        # Setup mock return values
        mock_exists.return_value = True
        creds = MagicMock()
        creds.valid = True
        mock_pickle_load.return_value = creds
        
        # Mock Gmail API response
        service = MagicMock()
        messages = [
            {'id': '1', 'snippet': 'Test message 1'},
            {'id': '2', 'snippet': 'Test message 2'}
        ]
        service.users().messages().list().execute.return_value = {'messages': messages}
        service.users().messages().get().execute.side_effect = [
            {'payload': {'headers': [{'name': 'Date', 'value': 'Mon, 1 Jan 2023 00:00:00 -0000'},
                                     {'name': 'From', 'value': 'test1@example.com'}]},
             'snippet': 'Test message 1'},
            {'payload': {'headers': [{'name': 'Date', 'value': 'Tue, 2 Jan 2023 00:00:00 -0000'},
                                     {'name': 'From', 'value': 'test2@example.com'}]},
             'snippet': 'Test message 2'}
        ]
        mock_build.return_value = service
        
        # Call the function and check the results
        messages = main.get_gmail_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0][1], 'test2@example.com')
        self.assertEqual(messages[1][1], 'test1@example.com')
    
    @patch('main.pipeline')
    def test_analyze_message(self, mock_pipeline):
        # Mock pipeline
        pipe = MagicMock()
        pipe.return_value = [{'label': 'phishing', 'score': 0.9}]
        mock_pipeline.return_value = pipe
        
        # Create a sample message and call the analyze_message function
        sample_message = "This is a test phishing message."
        root = tk.Tk()
        right_text = tk.Text(root)
        main.right_text = right_text
        main.pipe = pipe
        main.analyze_message(sample_message)
        
        # Check the results in the right_text widget
        result_text = right_text.get(1.0, tk.END).strip()
        self.assertIn("phishing", result_text)
        self.assertIn("0.9000", result_text)
        
if __name__ == '__main__':
    unittest.main()
