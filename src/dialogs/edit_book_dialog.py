import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..database.books import MAX_ROOMS, MAX_SHELVES

class EditBookDialog:
    def __init__(self, parent, db, book_data, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать книгу")
        self.dialog.geometry("400x450")  # Еще увеличиваем
        self.db = db
        self.book_id = book_data['id']
        self.callback = callback

        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)

        # Поля ввода
        ttk.Label(frame, text="Название:").pack(pady=(0, 5))
        self.title_entry = ttk.Entry(frame)
        self.title_entry.insert(0, book_data['title'])
        self.title_entry.pack(fill='x', pady=(0, 10))

        ttk.Label(frame, text="Автор:").pack(pady=(0, 5))
        self.author_entry = ttk.Entry(frame)
        self.author_entry.insert(0, book_data['author'])
        self.author_entry.pack(fill='x', pady=(0, 10))

        ttk.Label(frame, text="Издательство:").pack(pady=(0, 5))
        self.publisher_var = tk.StringVar()
        self.publisher_combobox = ttk.Combobox(frame, textvariable=self.publisher_var)

        self.update_publisher_list()  # Обновляем список
        self.publisher_combobox.pack(fill='x', pady=(0, 10))
        # Пытаемся установить текущее издательство
        self.set_current_publisher(book_data.get('publisher_id'))


        ttk.Label(frame, text="ID стеллажа:").pack(pady=(0, 5))
        self.shelf_entry = ttk.Entry(frame)
        self.shelf_entry.insert(0, book_data['shelf_id'])
        self.shelf_entry.pack(fill='x', pady=(0, 10))

        ttk.Label(frame, text="ID помещения:").pack(pady=(0, 5))
        self.room_entry = ttk.Entry(frame)
        self.room_entry.insert(0, book_data['room_id'])
        self.room_entry.pack(fill='x', pady=(0, 10))

        # Радиокнопки для статуса
        ttk.Label(frame, text="Статус книги:").pack(pady=(10, 5))
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill='x', pady=(0, 10))

        self.status_var = tk.StringVar()
        self.status_var.set(book_data['status'])

        statuses = [("Доступна", "доступна"),
                    ("Забронирована", "забронирована"),
                    ("Выдана", "выдана")]

        for text, value in statuses:
            ttk.Radiobutton(status_frame, text=text, value=value,
                            variable=self.status_var).pack(anchor=tk.W)

        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="Сохранить",
            command=self.save_changes
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Отмена",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def update_publisher_list(self):
        """Обновляет список издательств в комбобоксе."""
        publishers = self.db.books.get_publishers()
        publisher_names = [p.name for p in publishers]
        self.publisher_combobox['values'] = publisher_names
        if not publisher_names:
             self.publisher_var.set("")


    def set_current_publisher(self, publisher_id):
        """Устанавливает текущее выбранное издательство в combobox."""
        if publisher_id:
            try:
                # Получаем имя издательства по ID
                publisher_name = self.db.execute_query("SELECT name FROM publishers WHERE id = ?", (publisher_id,), fetchone=True)

                if publisher_name:
                    # Устанавливаем значение в combobox
                    self.publisher_var.set(publisher_name['name'])
            except sqlite3.Error:
                pass


    def save_changes(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        shelf_id = self.shelf_entry.get().strip()
        room_id = self.room_entry.get().strip()
        status = self.status_var.get()
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

        book_data = {
            'title': title,
            'author': author,
            'shelf_id': shelf_id,
            'room_id': room_id,
            'status': status,
            'publisher_id': publisher_id  # Добавлено
        }
        if self.db.books.edit_book(self.book_id, book_data):
            messagebox.showinfo("Успех", "Книга успешно отредактирована!")
            self.dialog.destroy()
            if self.callback:
                self.callback()
        else:
            messagebox.showerror("Ошибка", "Не удалось отредактировать книгу! Возможно, на этом стеллаже уже 250 книг.")