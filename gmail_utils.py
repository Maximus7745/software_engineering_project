import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
from datetime import timezone
from config import token_name, SCOPES

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(token_name, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def fetch_gmail_messages(service, max_results=10):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    message_list = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = msg['payload']['headers']
        date, sender = None, None
        for header in headers:
            if header['name'] == 'Date':
                date = parsedate_to_datetime(header['value']).astimezone(timezone.utc)
            if header['name'] == 'From':
                sender = header['value']
        if date and sender:
            snippet = msg['snippet']
            message_list.append((date, sender, snippet))

    message_list.sort(key=lambda x: x[0], reverse=True)
    return message_list[:10]
