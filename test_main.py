import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
import main
import tempfile
import os

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

        # Create a temporary token.pickle file
        with tempfile.NamedTemporaryFile(delete=False) as temp_token:
            temp_token_name = temp_token.name

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
        try:
            messages = main.get_gmail_messages()
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0][1], 'test2@example.com')
            self.assertEqual(messages[1][1], 'test1@example.com')
        finally:
            os.remove(temp_token_name)
    
    @patch('main.pipeline')
    @patch('tkinter.Text')
    @patch('tkinter.Tk')
    def test_analyze_message(self, mock_tk, mock_text, mock_pipeline):
        # Mock pipeline
        pipe = MagicMock()
        pipe.return_value = [{'label': 'phishing', 'score': 0.9}]
        mock_pipeline.return_value = pipe
        
        # Create a mock Text widget and root
        mock_text_instance = Mock()
        mock_text.return_value = mock_text_instance
        mock_root = Mock()
        mock_tk.return_value = mock_root

        # Create a sample message and call the analyze_message function
        sample_message = "This is a test phishing message."
        main.right_text = mock_text_instance
        main.pipe = pipe
        main.analyze_message(sample_message)
        
        # Check the results in the right_text widget
        mock_text_instance.insert.assert_called_once()
        args, kwargs = mock_text_instance.insert.call_args
        self.assertIn("phishing", args[1])
        self.assertIn("0.9000", args[1])
        
if __name__ == '__main__':
    unittest.main()
