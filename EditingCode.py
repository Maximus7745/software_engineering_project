import tkinter as tk
from tkinter import ttk
from transformers import pipeline


# Функция для создания закругленных прямоугольников
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
    # Очистка канвасов
    left_canvas.delete("all")
    right_canvas.delete("all")

    # Получение текущих размеров канвасов
    left_width = left_canvas.winfo_width()
    left_height = left_canvas.winfo_height()
    right_width = right_canvas.winfo_width()
    right_height = right_canvas.winfo_height()

    # Рисование закругленных прямоугольников
    left_canvas.create_polygon(create_rounded_rectangle(left_canvas, 0, 0, left_width, left_height, radius=25),
                               fill="#a9a9a9", outline="#000")
    right_canvas.create_polygon(create_rounded_rectangle(right_canvas, 0, 0, right_width, right_height, radius=25),
                                fill="#a9a9a9", outline="#000")


root = tk.Tk()
root.title("Phishing Detection Interface")
root.geometry("800x600")
root.configure(bg="#d3d3d3")

# Настройка сетки
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=4)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)

# Фрейм для ввода сообщения
email_frame = ttk.Frame(root, style="TFrame")
email_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

email_label = ttk.Label(email_frame, text="Введите сообщение:", style="TLabel")
email_label.grid(column=0, row=0, padx=10, pady=10)

email_entry = ttk.Entry(email_frame, width=100)
email_entry.grid(column=1, row=0, padx=10, pady=5, sticky="ew")
email_frame.grid_columnconfigure(1, weight=1)

# Кнопка для анализа сообщения
analyze_button = ttk.Button(email_frame, text="Анализировать", command=lambda: analyze_message(email_entry.get()))
analyze_button.grid(column=2, row=0, padx=10, pady=5)

# Левая область
left_canvas = tk.Canvas(root, bg="#a9a9a9", bd=0, highlightthickness=0, relief='ridge')
left_canvas.grid(row=1, column=0, padx=20, pady=10, sticky="nsew", rowspan=2)
root.grid_rowconfigure(1, weight=1)  # Ensure the row with the canvas can expand
root.grid_columnconfigure(0, weight=1)  # Ensure the column with the canvas can expand

# Текстовый виджет для отображения сообщений
left_text = tk.Text(left_canvas, wrap=tk.WORD, bg="#a9a9a9", relief='flat', cursor="hand2")
left_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Правая область
right_canvas = tk.Canvas(root, bg="#a9a9a9", bd=0, highlightthickness=0, relief='ridge')
right_canvas.grid(row=1, column=1, padx=20, pady=10, sticky="nsew", rowspan=2)
root.grid_rowconfigure(1, weight=1)  # Ensure the row with the canvas can expand
root.grid_columnconfigure(1, weight=1)  # Ensure the column with the canvas can expand

# Текстовый виджет для отображения результатов
right_text = tk.Text(right_canvas, wrap=tk.WORD, bg="#a9a9a9", relief='flat')
right_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Инициализация модели
pipe = pipeline("text-classification", model="ealvaradob/bert-finetuned-phishing")

right_text.tag_configure("red", foreground="red")
right_text.tag_configure("green", foreground="green")

left_text.tag_configure('message_box', borderwidth=1, relief="solid", lmargin1=10, lmargin2=10, rmargin=10,
                        font=("Courier", 10, "bold"))
left_text.tag_configure('spacing', lmargin1=10, lmargin2=10)
left_text.tag_configure('heading', font=("Helvetica", 12, "bold"), foreground="#0000FF")

# Счетчик сообщений
message_counter = 1

# Словарь для хранения результатов анализа
analysis_results = {}


# Функция для анализа введенного сообщения
def analyze_message(message):
    global message_counter

    result = pipe(message)[0]
    label = 'phishing' if result['label'] == 'phishing' else 'benign'
    color = "red" if label == 'phishing' else "green"
    score = result['score']

    left_text.insert(tk.END, f"Вам пришло сообщение {message_counter}:\n", 'heading')
    start_index = left_text.index(tk.END)
    left_text.insert(tk.END, f"\n{message}\n", 'message_box')
    left_text.insert(tk.END, "\n\n", 'spacing')
    end_index = left_text.index(tk.END)
    left_text.tag_add(f"clickable_{message_counter}", start_index, end_index)
    left_text.tag_bind(f"clickable_{message_counter}", "<Button-1>",
                       lambda e, msg_num=message_counter: display_result(msg_num))

    analysis_results[message_counter] = (label, score)
    message_counter += 1

    right_text.delete(1.0, tk.END)
    right_text.insert(tk.END, f"Введенное сообщение: {label} ({score:.4f})\n", color)


# Функция для отображения результата в правом текстовом виджете
def display_result(message_number):
    label, score = analysis_results[message_number]
    color = "red" if label == 'phishing' else "green"
    right_text.delete(1.0, tk.END)
    right_text.insert(tk.END, f"Сообщение {message_number}: {label} ({score:.4f})\n", color)


# Перерисовка прямоугольников при изменении размеров окна
root.bind("<Configure>", lambda event: draw_rounded_rectangles())

root.mainloop()
