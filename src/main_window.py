import tkinter as tk
from tkinter import ttk, messagebox
from .models import UserRole
from .search_engine import SearchType
from .dialogs.add_book_dialog import AddBookDialog
from .dialogs.edit_book_dialog import EditBookDialog
from .dialogs.journal_dialogs import (
    LoanJournalDialog,
    ReturnJournalDialog,
    ReservationJournalDialog
)
from .dialogs.librarian_dialog import LibrarianListDialog
from .dialogs.publisher_dialog import PublisherRequestDialog
from .auth_window import AuthWindow
from datetime import datetime
import sqlite3

class MainWindow:
    def __init__(self, db, root, user_role, current_user=None):
        self.db = db
        self.root = root
        self.current_user_role = user_role
        self.current_user = current_user
        self.tree = None
        self.button_frame = None
        self.search_type_var = None  #  Убираем
        self.room_var = None
        self.shelf_var = None
        self.shelf_combobox = None
        self.books_count_label = None
        self.search_entry = None # Добавляем
        self.show_books_window()

    def show_books_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("1050x550")

        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        # Фрейм для поиска и фильтров
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Тип поиска (теперь комбобокс)
        search_type_frame = ttk.Frame(search_frame)
        search_type_frame.pack(fill=tk.X)

        self.search_type_var = tk.StringVar(value=SearchType.TITLE.value)  # По умолчанию - поиск по названию
        search_type_combobox = ttk.Combobox(search_type_frame, textvariable=self.search_type_var,
                                            values=[SearchType.TITLE.value, SearchType.AUTHOR.value],
                                            state='readonly')  # Только для чтения
        search_type_combobox.pack(side=tk.LEFT, padx=5)
        search_type_combobox.set("По названию")  # Устанавливаем начальное значение


        # Поле поиска и кнопка
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=5)

        self.search_entry = ttk.Entry(search_input_frame) #Сохраняем
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(search_input_frame, text="Поиск",
                   command=lambda: self.search_books(
                       self.search_entry.get(),
                       SearchType(self.search_type_var.get()) #Исправлено
                   )).pack(side=tk.LEFT)

        # Фрейм для выбора помещения и стеллажа
        location_frame = ttk.Frame(top_frame)
        location_frame.pack(side=tk.LEFT, padx=20)

        # Выбор помещения
        ttk.Label(location_frame, text="Помещение:").pack(side=tk.LEFT, padx=(0, 5))
        self.room_var = tk.StringVar()
        room_combobox = ttk.Combobox(location_frame, textvariable=self.room_var,
                                     values=['1', '2', '3'], width=5, state='readonly')
        room_combobox.pack(side=tk.LEFT, padx=(0, 10))
        room_combobox.bind('<<ComboboxSelected>>', self.on_room_selected)

        # Выбор стеллажа
        ttk.Label(location_frame, text="Стеллаж:").pack(side=tk.LEFT, padx=(0, 5))
        self.shelf_var = tk.StringVar()
        self.shelf_combobox = ttk.Combobox(location_frame, textvariable=self.shelf_var,
                                           width=5, state='disabled')
        self.shelf_combobox.pack(side=tk.LEFT, padx=(0, 10))
        self.shelf_combobox.bind('<<ComboboxSelected>>', self.on_shelf_selected)

        # Счетчик книг
        self.books_count_label = ttk.Label(location_frame, text="")
        self.books_count_label.pack(side=tk.LEFT, padx=5)

        # Кнопка выхода
        ttk.Button(top_frame, text="Выход",
                   command=self.logout).pack(side=tk.RIGHT)

        # Основной контент
        content_frame = ttk.Frame(self.root, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Таблица книг  -  добавлено publisher_id
        self.tree = ttk.Treeview(content_frame, columns=(
            'title', 'author', 'status', 'shelf_id', 'room_id', 'id', 'publisher_id'
        ), show='headings')

        # Настройка колонок
        self.tree.heading('title', text='Название')
        self.tree.heading('author', text='Автор')
        self.tree.heading('status', text='Статус')
        self.tree.heading('shelf_id', text='Стеллаж')
        self.tree.heading('room_id', text='Помещение')
        self.tree.heading('id', text='ID')
        self.tree.heading('publisher_id', text='Издательство') #Добавлено

        self.tree.column('title', width=300)
        self.tree.column('author', width=200)
        self.tree.column('status', width=100)
        self.tree.column('shelf_id', width=70)
        self.tree.column('room_id', width=80)
        self.tree.column('id', width=50)
        self.tree.column('publisher_id', width=100)  # Добавлено

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Размещение таблицы и полосы прокрутки
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Нижняя панель с кнопками
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)

        # Кнопки действий
        self.button_frame = ttk.Frame(bottom_frame)
        self.button_frame.pack(side=tk.LEFT)

        if self.current_user_role in [UserRole.ADMIN, UserRole.OWNER]:
            ttk.Button(self.button_frame, text="Добавить книгу",
                       command=self.show_add_book_dialog).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.button_frame, text="Редактировать книгу",
                       command=self.show_edit_book_dialog).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.button_frame, text="Удалить книгу",
                       command=self.delete_book).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.button_frame, text="Обращение к издательству",
                       command=lambda: PublisherRequestDialog(self.root, self.db)
                       ).pack(side=tk.LEFT, padx=5)

            # Журналы
            journal_frame = ttk.Frame(bottom_frame)
            journal_frame.pack(side=tk.RIGHT)

            ttk.Button(journal_frame, text="Журнал выдачи",
                       command=lambda: LoanJournalDialog(self.root, self.db)
                       ).pack(side=tk.LEFT, padx=5)

            ttk.Button(journal_frame, text="Журнал возврата",
                       command=lambda: ReturnJournalDialog(self.root, self.db)
                       ).pack(side=tk.LEFT, padx=5)

            ttk.Button(journal_frame, text="Журнал резервирования",
                       command=lambda: ReservationJournalDialog(self.root, self.db)
                       ).pack(side=tk.LEFT, padx=5)

            if self.current_user_role == UserRole.OWNER:
                ttk.Button(journal_frame, text="Библиотекари",
                           command=lambda: LibrarianListDialog(self.root, self.db)
                           ).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(self.button_frame, text="Забронировать",
                       command=self.reserve_book).pack(side=tk.LEFT, padx=5)

        # Загрузка данных
        self.search_books()

    def on_room_selected(self, event):
        room = self.room_var.get()
        if room:
            self.shelf_combobox['values'] = ['1', '2', '3', '4', '5']
            self.shelf_combobox['state'] = 'readonly'
            self.shelf_var.set('')  # Сброс выбора стеллажа
            self.books_count_label['text'] = ''
            self.search_books()  # Обновляем список книг для выбранного помещения
        else:
            self.shelf_combobox['state'] = 'disabled'
            self.shelf_var.set('')
            self.books_count_label['text'] = ''

    def on_shelf_selected(self, event):
        room = self.room_var.get()
        shelf = self.shelf_var.get()
        if room and shelf:
            # Получаем количество книг на выбранном стеллаже
            total_books = self.db.books.count_books_in_shelf(int(room), int(shelf))
            self.books_count_label['text'] = f"Книг на стеллаже: {total_books}/250"
            self.search_books()  # Обновляем список книг для выбранного стеллажа
    def search_books(self, search_term="", search_type=SearchType.TITLE): #Изменено
        self.tree.delete(*self.tree.get_children())

        # Получаем выбранное помещение и стеллаж
        room = self.room_var.get() if self.room_var.get() else None
        shelf = self.shelf_var.get() if self.shelf_var.get() else None

        # Получаем книги с учетом фильтров
        books = self.db.books.get_books(
            search_term=search_term,
            room_id=int(room) if room else None,
            shelf_id=int(shelf) if shelf else None,
            search_type=search_type  # Передаем search_type
        )

        for book in books:
            publisher_name = ""
            if book.publisher_id:
                try:
                    pub_name = self.db.execute_query("SELECT name from publishers WHERE id = ?", (book.publisher_id,), fetchone=True)
                    publisher_name = pub_name['name'] if pub_name else "Неизвестно"

                except sqlite3.Error:
                    publisher_name = "Неизвестно"

            self.tree.insert('', 'end', values=(
                book.title,
                book.author,
                book.status,
                book.shelf_id,
                book.room_id,
                book.id,
                publisher_name # Добавлено
            ))

    def show_add_book_dialog(self):
        AddBookDialog(self.root, self.db, self.search_books)

    def show_edit_book_dialog(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите книгу для редактирования!")
            return

        item = self.tree.item(selection[0])
        # Добавлено извлечение publisher_id (индекс 6)
        book_data = {
            'id': item['values'][5],
            'title': item['values'][0],
            'author': item['values'][1],
            'status': item['values'][2],
            'shelf_id': item['values'][3],
            'room_id': item['values'][4],
            'publisher_id': item['values'][6] if len(item['values']) > 6 else None,  # Добавлено

        }

        EditBookDialog(self.root, self.db, book_data, self.search_books)

    def reserve_book(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите книгу!")
            return

        item = self.tree.item(selection[0])
        if item['values'][2] != "Доступна":
            messagebox.showwarning("Предупреждение", "Книга недоступна для бронирования!")
            return

        book_id = item['values'][5]
        shelf_id = item['values'][3]
        room_id = item['values'][4]
        current_time = datetime.now()  # Получаем текущее время

        # Резервируем книгу
        if self.db.books.reserve_book(book_id, self.current_user.id, shelf_id, room_id):
            # Добавляем запись в журнал резервирования
            reservation_period = 14  # дней

            if self.db.journals.add_reservation(
                    book_id=book_id,
                    shelf_id=shelf_id,
                    room_id=room_id,
                    reader_id=self.current_user.id,
                    reservation_date=current_time.isoformat(),
                    reservation_period=reservation_period
            ):
                self.search_books()
                messagebox.showinfo("Бронирование",
                                    f"Книга успешно забронирована на {reservation_period} дней!")
            else:
                messagebox.showwarning("Предупреждение",
                                       "Книга забронирована, но не удалось создать запись в журнале!")
        else:
            messagebox.showerror("Ошибка", "Не удалось забронировать книгу!")

    def delete_book(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту книгу?"):
            item = self.tree.item(selection[0])
            book_id = item['values'][5]
            if self.db.books.delete_book(book_id):
                self.search_books()
                messagebox.showinfo("Успех", "Книга удалена!")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить книгу!")

    def logout(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из аккаунта?"):
            for widget in self.root.winfo_children():
                widget.destroy()
            auth_window = AuthWindow(self.db, lambda role, user: self.__init__(self.db, self.root, role, user))
            auth_window.show_login_window(self.root)