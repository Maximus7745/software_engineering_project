import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Области доступа, которые нужны для работы с API Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # Файл token.pickle хранит токен доступа пользователя и обновляется автоматически
    # при каждом запуске программы
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Если нет действительных учетных данных, выполните вход пользователя
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_364975786693-oc6g8gie5bsjgqbrlbe4ns15l0t6fgsh.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраните учетные данные для следующего запуска
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Создание объекта службы API Gmail
    service = build('gmail', 'v1', credentials=creds)

    # Вызов Gmail API для получения списка сообщений
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
        print('Messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            print(f"Message snippet: {msg['snippet']}")

if __name__ == '__main__':
    main()
