import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..database.books import MAX_ROOMS, MAX_SHELVES

class AddBookDialog:
    def __init__(self, parent, db, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить книгу")
        self.dialog.geometry("400x400")  # Увеличиваем высоту
        self.db = db
        self.callback = callback

        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)

        # Поля ввода
        ttk.Label(frame, text="Название:").pack(pady=(0, 5))
        self.title_entry = ttk.Entry(frame)
        self.title_entry.pack(fill='x', pady=(0, 10))

        ttk.Label(frame, text="Автор:").pack(pady=(0, 5))
        self.author_entry = ttk.Entry(frame)
        self.author_entry.pack(fill='x', pady=(0, 10))

        ttk.Label(frame, text="Издательство:").pack(pady=(0, 5))
        self.publisher_var = tk.StringVar()
        self.publisher_combobox = ttk.Combobox(frame, textvariable=self.publisher_var)
        self.update_publisher_list()  # Заполняем комбобокс
        self.publisher_combobox.pack(fill='x', pady=(0, 10))


        ttk.Label(frame, text="ID стеллажа:").pack(pady=(0, 5))
        self.shelf_entry = ttk.Entry(frame)
        self.shelf_entry.pack(fill='x', pady=(0, 10))
        self.shelf_entry.insert(0, "1")

        ttk.Label(frame, text="ID помещения:").pack(pady=(0, 5))
        self.room_entry = ttk.Entry(frame)
        self.room_entry.pack(fill='x', pady=(0, 10))
        self.room_entry.insert(0, "1")

        ttk.Button(frame, text="Добавить", command=self.add_book).pack(pady=20)

    def update_publisher_list(self):
        """Обновляет список издательств в комбобоксе."""
        publishers = self.db.books.get_publishers()
        publisher_names = [p.name for p in publishers]
        self.publisher_combobox['values'] = publisher_names
        if publisher_names:
            self.publisher_combobox.current(0) #Выбираем первый элемент
        else:
            self.publisher_var.set("")  # Очищаем, если список пуст

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        shelf_id = self.shelf_entry.get().strip()
        room_id = self.room_entry.get().strip()
        publisher_name = self.publisher_var.get().strip()


        if not all([title, author, shelf_id, room_id, publisher_name]):
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return

        try:
            shelf_id = int(shelf_id)
            room_id = int(room_id)
        except ValueError:
            messagebox.showerror("Ошибка", "ID стеллажа и помещения должны быть числами!")
            return

        # Получаем ID издательства (или добавляем новое)
        try:
            publisher_id = self.db.books.add_publisher(publisher_name)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при работе с издательством: {e}")
            return


        if not (1 <= room_id <= MAX_ROOMS and 1 <= shelf_id <= MAX_SHELVES):
            messagebox.showerror("Ошибка", f"ID помещения должен быть от 1 до {MAX_ROOMS}, ID стеллажа - от 1 до {MAX_SHELVES}!")
            return

        if self.db.books.add_book(title, author, shelf_id, room_id, publisher_id):
            messagebox.showinfo("Успех", "Книга добавлена!")
            self.dialog.destroy()
            if self.callback:
                self.callback()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить книгу! Возможно, на этом стеллаже уже 250 книг.")