import tkinter as tk
from tkinter import ttk, messagebox


class PublisherRequestDialog:
    def __init__(self, parent, db):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Обращение к издательству")
        self.dialog.geometry("400x400")
        self.db = db

        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)

        # Выбор издательства
        ttk.Label(frame, text="Выберите издательство:").pack(pady=(0, 5))
        publishers = self.db.books.get_publishers()
        self.publisher_var = tk.StringVar()
        publisher_combo = ttk.Combobox(frame, textvariable=self.publisher_var)
        publisher_combo['values'] = [p.name for p in publishers]
        publisher_combo.pack(fill='x', pady=(0, 10))
        if publishers:
            publisher_combo.set(publishers[0].name)

        # Текст обращения
        ttk.Label(frame, text="Текст обращения:").pack(pady=(0, 5))
        self.text_widget = tk.Text(frame, height=10, width=40)
        self.text_widget.pack(fill='both', expand=True, pady=(0, 10))

        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(0, 5))

        ttk.Button(button_frame, text="Отправить",
                   command=self.send_request).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Отмена",
                   command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def send_request(self):
        publisher = self.publisher_var.get()
        text = self.text_widget.get("1.0", "end-1c")

        if not publisher or not text.strip():
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return

        # В реальном приложении здесь был бы код отправки запроса
        messagebox.showinfo("Успех", "Обращение отправлено издательству!")
        self.dialog.destroy()