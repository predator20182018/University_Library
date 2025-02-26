import tkinter as tk
from tkinter import ttk, messagebox


class LoanJournalDialog:
    def __init__(self, parent, db):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Журнал выдачи книг")
        self.dialog.geometry("825x600")
        self.db = db

        # Создаем таблицу
        self.tree = ttk.Treeview(self.dialog, columns=(
            'id', 'librarian', 'reader', 'book',
            'shelf', 'room', 'date'
        ), show='headings')

        # Заголовки колонок
        self.tree.heading('id', text='ID')
        self.tree.heading('librarian', text='Библиотекарь')
        self.tree.heading('reader', text='Читатель')
        self.tree.heading('book', text='Книга')
        self.tree.heading('shelf', text='Стеллаж')
        self.tree.heading('room', text='Помещение')
        self.tree.heading('date', text='Дата выдачи')

        # Настройка ширины колонок
        self.tree.column('id', width=50)
        self.tree.column('librarian', width=150)
        self.tree.column('reader', width=150)
        self.tree.column('book', width=200)
        self.tree.column('shelf', width=80)
        self.tree.column('room', width=80)
        self.tree.column('date', width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопка очистки журнала
        ttk.Button(self.dialog, text="Очистить журнал",
                   command=self.clear_journal).pack(pady=5)

        # Загружаем данные
        self.load_data()

    def clear_journal(self):
        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите очистить журнал выдачи?\n"
                               "Это действие нельзя отменить!"):
            if self.db.journals.clear_loan_journal():
                messagebox.showinfo("Успех", "Журнал выдачи очищен!")
                self.load_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось очистить журнал!")

    def load_data(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Загружаем записи из журнала
        loans = self.db.journals.get_loans()
        for loan in loans:
            self.tree.insert('', 'end', values=(
                loan[0],  # id
                f"ID: {loan[1]}",  # librarian_id
                f"ID: {loan[2]}",  # reader_id
                f"ID: {loan[3]}",  # book_id
                loan[4],  # shelf_id
                loan[5],  # room_id
                loan[6]  # loan_date
            ))


class ReturnJournalDialog:
    def __init__(self, parent, db):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Журнал возврата книг")
        self.dialog.geometry("1025x600")
        self.db = db

        # Создаем таблицу
        self.tree = ttk.Treeview(self.dialog, columns=(
            'id', 'loan_id', 'librarian', 'reader', 'book',
            'shelf', 'room', 'date', 'overdue'
        ), show='headings')

        # Заголовки колонок
        self.tree.heading('id', text='ID')
        self.tree.heading('loan_id', text='ID выдачи')
        self.tree.heading('librarian', text='Библиотекарь')
        self.tree.heading('reader', text='Читатель')
        self.tree.heading('book', text='Книга')
        self.tree.heading('shelf', text='Стеллаж')
        self.tree.heading('room', text='Помещение')
        self.tree.heading('date', text='Дата возврата')
        self.tree.heading('overdue', text='Дней просрочки')

        # Настройка ширины колонок
        self.tree.column('id', width=50)
        self.tree.column('loan_id', width=80)
        self.tree.column('librarian', width=150)
        self.tree.column('reader', width=150)
        self.tree.column('book', width=200)
        self.tree.column('shelf', width=80)
        self.tree.column('room', width=80)
        self.tree.column('date', width=100)
        self.tree.column('overdue', width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопка очистки журнала
        ttk.Button(self.dialog, text="Очистить журнал",
                   command=self.clear_journal).pack(pady=5)

        # Загружаем данные
        self.load_data()

    def clear_journal(self):
        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите очистить журнал возврата?\n"
                               "Это действие нельзя отменить!"):
            if self.db.journals.clear_return_journal():
                messagebox.showinfo("Успех", "Журнал возврата очищен!")
                self.load_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось очистить журнал!")

    def load_data(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Загружаем записи из журнала
        returns = self.db.journals.get_returns()
        for return_record in returns:
            self.tree.insert('', 'end', values=(
                return_record[0],  # id
                return_record[1],  # loan_id
                f"ID: {return_record[2]}",  # librarian_id
                f"ID: {return_record[3]}",  # reader_id
                f"ID: {return_record[4]}",  # book_id
                return_record[5],  # shelf_id
                return_record[6],  # room_id
                return_record[7],  # return_date
                return_record[8]  # overdue_days
            ))


class ReservationJournalDialog:
    def __init__(self, parent, db):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Журнал резервирования")
        self.dialog.geometry("925x600")
        self.db = db

        # Создаем таблицу
        self.tree = ttk.Treeview(self.dialog, columns=(
            'id', 'book', 'shelf', 'room', 'reader',
            'date', 'period', 'notified'
        ), show='headings')

        # Заголовки колонок
        self.tree.heading('id', text='ID')
        self.tree.heading('book', text='Книга')
        self.tree.heading('shelf', text='Стеллаж')
        self.tree.heading('room', text='Помещение')
        self.tree.heading('reader', text='Читатель')
        self.tree.heading('date', text='Дата резервирования')
        self.tree.heading('period', text='Период (дней)')
        self.tree.heading('notified', text='Уведомлён')

        # Настройка ширины колонок
        self.tree.column('id', width=50)
        self.tree.column('book', width=200)
        self.tree.column('shelf', width=80)
        self.tree.column('room', width=80)
        self.tree.column('reader', width=150)
        self.tree.column('date', width=150)
        self.tree.column('period', width=100)
        self.tree.column('notified', width=80)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопка очистки журнала
        ttk.Button(self.dialog, text="Очистить журнал",
                   command=self.clear_journal).pack(pady=5)

        # Загружаем данные
        self.load_data()

    def clear_journal(self):
        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите очистить журнал резервирования?\n"
                               "Это действие нельзя отменить!"):
            if self.db.journals.clear_reservation_journal():
                messagebox.showinfo("Успех", "Журнал резервирования очищен!")
                self.load_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось очистить журнал!")

    def load_data(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Загружаем записи из журнала
        reservations = self.db.journals.get_reservations()
        for reservation in reservations:
            self.tree.insert('', 'end', values=(
                reservation[0],  # id
                f"ID: {reservation[1]}",  # book_id
                reservation[2],  # shelf_id
                reservation[3],  # room_id
                f"ID: {reservation[4]}",  # reader_id
                reservation[5],  # reservation_date
                reservation[6],  # reservation_period
                "Да" if reservation[7] else "Нет"  # notification_sent
            ))