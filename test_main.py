import pytest
from unittest.mock import patch, MagicMock
from your_module import get_gmail_messages, analyze_message  # замените your_module на имя вашего файла без .py

@patch('your_module.build')
@patch('your_module.Credentials')
@patch('your_module.InstalledAppFlow')
@patch('your_module.pickle')
@patch('your_module.os.path')
def test_get_gmail_messages(mock_os_path, mock_pickle, mock_installed_app_flow, mock_credentials, mock_build):
    # Мокаем данные
    mock_os_path.exists.return_value = False
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.expired = False
    mock_creds.refresh_token = None
    mock_credentials.return_value = mock_creds
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    messages = {
        'messages': [
            {'id': '1'},
            {'id': '2'},
        ]
    }
    message = {
        'payload': {
            'headers': [
                {'name': 'Date', 'value': 'Mon, 1 Jan 2020 00:00:00 -0000'},
                {'name': 'From', 'value': 'test@example.com'}
            ]
        },
        'snippet': 'Test snippet'
    }
    mock_service.users().messages().list().execute.return_value = messages
    mock_service.users().messages().get().execute.return_value = message

    result = get_gmail_messages()
    assert len(result) == 2
    assert result[0][1] == 'test@example.com'
    assert result[0][2] == 'Test snippet'

@patch('your_module.pipeline')
def test_analyze_message(mock_pipeline):
    mock_pipeline.return_value = MagicMock(return_value=[{'label': 'phishing', 'score': 0.95}])
    message = "This is a phishing test message."
    result = analyze_message(message)
    assert result[0]['label'] == 'phishing'
    assert result[0]['score'] == 0.95
