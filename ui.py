import tkinter as tk
from tkinter import ttk
from gmail_utils import get_gmail_service, fetch_gmail_messages
from text_analysis import TextAnalyzer
from config import CHECK_INTERVAL


class PhishingDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Detection Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="#d3d3d3")

        self.text_analyzer = TextAnalyzer()
        self.analysis_results = {}
        self.message_counter = 1

        self.setup_ui()

        self.service = get_gmail_service()
        self.fetch_and_display_messages()

    def setup_ui(self):
        self.email_frame = ttk.Frame(self.root, style="TFrame")
        self.email_frame.grid(row=0, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        self.email_label = ttk.Label(self.email_frame, text="Введите сообщение:", style="TLabel")
        self.email_label.grid(column=0, row=0, padx=10, pady=10)

        self.email_entry = ttk.Entry(self.email_frame, width=100)
        self.email_entry.grid(column=1, row=0, padx=10, pady=5, sticky="ew")
        self.email_frame.grid_columnconfigure(1, weight=1)

        self.analyze_button = ttk.Button(self.email_frame, text="Анализировать", command=self.analyze_entry_message)
        self.analyze_button.grid(column=2, row=0, padx=10, pady=5)

        self.left_canvas = tk.Canvas(self.root, bg="#a9a9a9", bd=0, highlightthickness=0, relief='ridge')
        self.left_canvas.grid(row=1, column=0, padx=20, pady=10, sticky="nsew", rowspan=2)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.left_text = tk.Text(self.left_canvas, wrap=tk.WORD, bg="#a9a9a9", relief='flat', cursor="hand2",
                                 state='disabled')
        self.left_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.right_canvas = tk.Canvas(self.root, bg="#a9a9a9", bd=0, highlightthickness=0, relief='ridge')
        self.right_canvas.grid(row=1, column=2, padx=20, pady=10, sticky="nsew", rowspan=2)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        self.right_text = tk.Text(self.right_canvas, wrap=tk.WORD, bg="#a9a9a9", relief='flat', state='disabled')
        self.right_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.right_text.tag_configure("red", foreground="red")
        self.right_text.tag_configure("green", foreground="green")

        self.left_text.tag_configure('message_box', borderwidth=1, relief="solid", lmargin1=10, lmargin2=10, rmargin=10,
                                     font=("Courier", 10, "bold"))
        self.left_text.tag_configure('spacing', lmargin1=10, lmargin2=10)
        self.left_text.tag_configure('heading', font=("Helvetica", 12, "bold"), foreground="#0000FF")
        self.left_text.tag_configure('sender', font=("Helvetica", 10, "bold"), foreground="#000000")
        self.left_text.tag_configure('date', font=("Helvetica", 10, "normal"), foreground="#008000")

        refresh_button = ttk.Button(self.root, text="⟳", command=self.display_messages, width=2)
        refresh_button.place(relx=0.5, rely=0.15, anchor="center")

        close_button = ttk.Button(self.root, text="✖", command=self.root.quit, width=2)
        close_button.place(relx=0.5, rely=0.95, anchor="center")

        self.root.bind("<Configure>", lambda event: self.draw_rounded_rectangles())

    def draw_rounded_rectangles(self):
        self.left_canvas.delete("all")
        self.right_canvas.delete("all")

        left_width = self.left_canvas.winfo_width()
        left_height = self.left_canvas.winfo_height()
        right_width = self.right_canvas.winfo_width()
        right_height = self.right_canvas.winfo_height()

        self.left_canvas.create_polygon(self.create_rounded_rectangle(0, 0, left_width, left_height, radius=25),
                                        fill="#a9a9a9", outline="#000")
        self.right_canvas.create_polygon(self.create_rounded_rectangle(0, 0, right_width, right_height, radius=25),
                                         fill="#a9a9a9", outline="#000")

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25):
        points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
                  x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius,
                  x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius,
                  y2, x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1]
        return points

    def analyze_entry_message(self):
        message = self.email_entry.get()
        self.analyze_message(message)

    def analyze_message(self, message):
        label, score = self.text_analyzer.analyze(message)
        color = "red" if label == 'phishing' else "green"

        self.right_text.configure(state='normal')
        self.right_text.delete(1.0, tk.END)
        self.right_text.insert(tk.END, f"Введенное сообщение: {label} ({score:.4f})\n", color)
        self.right_text.configure(state='disabled')

    def display_messages(self):
        self.message_counter = 1
        self.left_text.configure(state='normal')
        self.left_text.delete(1.0, tk.END)
        message_list = fetch_gmail_messages(self.service)
        if not message_list:
            self.left_text.insert(tk.END, "No messages found.\n", 'heading')
        else:
            for date, sender, snippet in message_list:
                self.insert_message(sender, date, snippet)
        self.left_text.configure(state='disabled')

    def insert_message(self, sender, date, message):
        self.left_text.configure(state='normal')
        self.left_text.insert(tk.END, f"Отправитель: {sender}\n", 'sender')
        self.left_text.insert(tk.END, f"Дата: {date.strftime('%Y-%m-%d %H:%M:%S')}\n", 'date')
        self.left_text.insert(tk.END, f"Вам пришло сообщение {self.message_counter}:\n", 'heading')
        start_index = self.left_text.index(tk.END)
        self.left_text.insert(tk.END, f"\n{message}\n", 'message_box')
        self.left_text.insert(tk.END, "\n\n", 'spacing')
        end_index = self.left_text.index(tk.END)
        self.left_text.tag_add(f"clickable_{self.message_counter}", start_index, end_index)
        self.left_text.tag_bind(f"clickable_{self.message_counter}", "<Button-1>",
                                lambda e, msg_num=self.message_counter: self.display_result(msg_num))
        self.left_text.configure(state='disabled')

        self.analysis_results[self.message_counter] = (message, None)
        self.message_counter += 1

    def display_result(self, message_number):
        message, _ = self.analysis_results[message_number]
        self.analyze_message(message)

    def fetch_and_display_messages(self):
        self.display_messages()
        self.root.after(CHECK_INTERVAL, self.fetch_and_display_messages)
