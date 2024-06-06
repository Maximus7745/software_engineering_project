import os.path
import pickle
import tkinter as tk
from tkinter import ttk
from transformers import pipeline
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
from datetime import timezone
from config import token_name

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CHECK_INTERVAL = 120000


def get_gmail_messages():
    """Fetch messages from Gmail."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                token_name, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=100).execute()
    messages = results.get('messages', [])
    message_list = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = msg['payload']['headers']
        date, sender = None, None
        for header in headers:
            if header['name'] == 'Date':
                date = parsedate_to_datetime(header['value'])
                date = date.astimezone(timezone.utc)
            if header['name'] == 'From':
                sender = header['value']
        if date and sender:
            snippet = msg['snippet']
            message_list.append((date, sender, snippet))

    message_list.sort(key=lambda x: x[0], reverse=True)

    return message_list[:10]


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1 + radius, y1,
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
    return points


def draw_rounded_rectangles():
    global left_canvas, right_canvas
    left_canvas.delete("all")
    right_canvas.delete("all")

    left_width = left_canvas.winfo_width()
    left_height = left_canvas.winfo_height()
    right_width = right_canvas.winfo_width()
    right_height = right_canvas.winfo_height()

    left_canvas.create_polygon(create_rounded_rectangle(left_canvas, 0, 0, left_width, left_height, radius=25),
                               fill="#a9a9a9", outline="#000")
    right_canvas.create_polygon(create_rounded_rectangle(right_canvas, 0, 0, right_width, right_height, radius=25),
                                fill="#a9a9a9", outline="#000")


def main():
    global left_canvas, right_canvas, left_text, right_text, message_counter
    root = tk.Tk()
    root.title("Phishing Detection Interface")
    root.geometry("800x600")
    root.configure(bg="#d3d3d3")

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=4)
    root.grid_columnconfigure(2, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)

    email_frame = ttk.Frame(root, style="TFrame")
    email_frame.grid(row=0, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

    email_label = ttk.Label(email_frame, text="Введите сообщение:", style="TLabel")
    email_label.grid(column=0, row=0, padx=10, pady=10)

    email_entry = ttk.Entry(email_frame, width=100)
    email_entry.grid(column=1, row=0, padx=10, pady=5, sticky="ew")
    email_frame.grid_columnconfigure(1, weight=1)

    analyze_button = ttk.Button(email_frame, text="Анализировать", command=lambda: analyze_message(email_entry.get()))
    analyze_button.grid(column=2, row=0, padx=10, pady=5)

    left_canvas = tk.Canvas(root, bg="#a9a9a9", bd=0, highlightthickness=0, relief='ridge')
    left_canvas.grid(row=1, column=0, padx=20, pady=10, sticky="nsew", rowspan=2)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    left_text = tk.Text(left_canvas, wrap=tk.WORD, bg="#a9a9a9", relief='flat', cursor="hand2", state='disabled')
    left_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    right_canvas = tk.Canvas(root, bg="#a9a9a9", bd=0, highlightthickness=0, relief='ridge')
    right_canvas.grid(row=1, column=2, padx=20, pady=10, sticky="nsew", rowspan=2)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

    right_text = tk.Text(right_canvas, wrap=tk.WORD, bg="#a9a9a9", relief='flat', state='disabled')
    right_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    pipe = pipeline("text-classification", model="ealvaradob/bert-finetuned-phishing")

    right_text.tag_configure("red", foreground="red")
    right_text.tag_configure("green", foreground="green")

    left_text.tag_configure('message_box', borderwidth=1, relief="solid", lmargin1=10, lmargin2=10, rmargin=10,
                            font=("Courier", 10, "bold"))
    left_text.tag_configure('spacing', lmargin1=10, lmargin2=10)
    left_text.tag_configure('heading', font=("Helvetica", 12, "bold"), foreground="#0000FF")
    left_text.tag_configure('sender', font=("Helvetica", 10, "bold"), foreground="#000000")
    left_text.tag_configure('date', font=("Helvetica", 10, "normal"), foreground="#008000")

    message_counter = 1
    analysis_results = {}

    def insert_message(sender, date, message):
        global message_counter
        left_text.configure(state='normal')
        left_text.insert(tk.END, f"Отправитель: {sender}\n", 'sender')
        left_text.insert(tk.END, f"Дата: {date.strftime('%Y-%m-%d %H:%M:%S')}\n", 'date')
        left_text.insert(tk.END, f"Вам пришло сообщение {message_counter}:\n", 'heading')
        start_index = left_text.index(tk.END)
        left_text.insert(tk.END, f"\n{message}\n", 'message_box')
        left_text.insert(tk.END, "\n\n", 'spacing')
        end_index = left_text.index(tk.END)
        left_text.tag_add(f"clickable_{message_counter}", start_index, end_index)
        left_text.tag_bind(f"clickable_{message_counter}", "<Button-1>",
                           lambda e, msg_num=message_counter: display_result(msg_num))
        left_text.configure(state='disabled')

        analysis_results[message_counter] = (message, None)
        message_counter += 1

    def analyze_message(message):
        result = pipe(message)[0]
        label = 'phishing' if result['label'] == 'phishing' else 'benign'
        color = "red" if label == 'phishing' else "green"
        score = result['score']

        right_text.configure(state='normal')
        right_text.delete(1.0, tk.END)
        right_text.insert(tk.END, f"Введенное сообщение: {label} ({score:.4f})\n", color)
        right_text.configure(state='disabled')

    def display_result(message_number):
        message, _ = analysis_results[message_number]
        analyze_message(message)

    def display_messages():
        global message_counter
        message_counter = 1
        left_text.configure(state='normal')
        left_text.delete(1.0, tk.END)
        message_list = get_gmail_messages()
        if not message_list:
            left_text.insert(tk.END, "No messages found.\n", 'heading')
        else:
            for date, sender, snippet in message_list:
                insert_message(sender, date, snippet)
        left_text.configure(state='disabled')

    def fetch_and_display_messages():
        display_messages()
        root.after(CHECK_INTERVAL, fetch_and_display_messages)

    refresh_button = ttk.Button(root, text="⟳", command=display_messages, width=2)
    refresh_button.place(relx=0.5, rely=0.15, anchor="center")

    close_button = ttk.Button(root, text="✖", command=root.quit, width=2)
    close_button.place(relx=0.5, rely=0.95, anchor="center")

    fetch_and_display_messages()

    root.bind("<Configure>", lambda event: draw_rounded_rectangles())
    root.mainloop()


if __name__ == '__main__':
    main()
