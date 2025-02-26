import tkinter as tk
from tkinter import ttk, messagebox
from ..models import UserRole, User


class LibrarianListDialog:
    def __init__(self, parent, db):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Список библиотекарей")
        self.dialog.geometry("800x600")
        self.db = db

        # Создаем таблицу библиотекарей
        self.tree = ttk.Treeview(self.dialog, columns=(
            'id', 'lastname', 'firstname', 'middlename',
            'phone', 'email', 'position'
        ), show='headings')

        # Заголовки колонок
        self.tree.heading('id', text='ID')
        self.tree.heading('lastname', text='Фамилия')
        self.tree.heading('firstname', text='Имя')
        self.tree.heading('middlename', text='Отчество')
        self.tree.heading('phone', text='Телефон')
        self.tree.heading('email', text='Email')
        self.tree.heading('position', text='Должность')

        # Настройка ширины колонок
        self.tree.column('id', width=50)
        self.tree.column('lastname', width=120)
        self.tree.column('firstname', width=120)
        self.tree.column('middlename', width=120)
        self.tree.column('phone', width=120)
        self.tree.column('email', width=150)
        self.tree.column('position', width=120)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки управления
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Добавить библиотекаря",
                   command=self.show_add_librarian_dialog).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Редактировать",
                   command=self.show_edit_librarian_dialog).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Удалить",
                   command=self.delete_librarian).pack(side=tk.LEFT, padx=5)

        # Загружаем данные
        self.load_data()

    def load_data(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Загружаем библиотекарей из базы
        librarians = self.db.users.get_librarians()
        for librarian in librarians:
            self.tree.insert('', 'end', values=(
                librarian.id,
                librarian.lastname,
                librarian.firstname,
                librarian.middlename,
                librarian.phone,
                librarian.email,
                librarian.position
            ))

    def show_add_librarian_dialog(self):
        AddLibrarianDialog(self.dialog, self.db, self.load_data)

    def show_edit_librarian_dialog(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите библиотекаря для редактирования!")
            return

        item = self.tree.item(selection[0])
        librarian_id = item['values'][0]
        librarian_data = {
            'id': librarian_id,
            'lastname': item['values'][1],
            'firstname': item['values'][2],
            'middlename': item['values'][3],
            'phone': item['values'][4],
            'email': item['values'][5],
            'position': item['values'][6]
        }
        EditLibrarianDialog(self.dialog, self.db, librarian_data, self.load_data)

    def delete_librarian(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите библиотекаря для удаления!")
            return

        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите удалить этого библиотекаря?\n"
                               "Это действие нельзя отменить!"):
            item = self.tree.item(selection[0])
            librarian_id = item['values'][0]

            if self.db.users.delete_librarian(librarian_id):
                messagebox.showinfo("Успех", "Библиотекарь успешно удален!")
                self.load_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить библиотекаря!")


class AddLibrarianDialog:
    def __init__(self, parent, db, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить библиотекаря")
        self.dialog.geometry("400x500")
        self.db = db
        self.callback = callback
        self.frame = ttk.Frame(self.dialog, padding="20")
        self.frame.pack(fill="both", expand=True)
        self.entries = {}
        self._create_fields()
        ttk.Button(self.frame, text="Добавить", command=self.add_librarian).pack(pady=20)



    def _create_entry_field(self, label_text, field_name, show=None):
        """Создает поле ввода с меткой."""
        ttk.Label(self.frame, text=label_text).pack(pady=(10, 0))
        entry = ttk.Entry(self.frame, show=show)
        entry.pack(fill='x', pady=(0, 5))
        self.entries[field_name] = entry

    def _create_fields(self):
        """Создает все поля ввода."""
        fields = [
            ('username', 'Логин', None),
            ('password', 'Пароль', "*"),
            ('lastname', 'Фамилия', None),
            ('firstname', 'Имя', None),
            ('middlename', 'Отчество', None),
            ('phone', 'Телефон', None),
            ('email', 'Email', None),
            ('position', 'Должность', None)
        ]

        for field_name, label_text, show_char in fields:
            self._create_entry_field(label_text, field_name, show_char)

    def add_librarian(self):
        try:
            # Проверяем заполнение всех полей
            for field, entry in self.entries.items():
                if not entry.get().strip():
                    raise ValueError(f"Поле {field} обязательно для заполнения")

            # Создаем объект User для нового библиотекаря
            librarian = User(
                username=self.entries['username'].get().strip(),
                password=self.entries['password'].get().strip(),
                lastname=self.entries['lastname'].get().strip(),
                firstname=self.entries['firstname'].get().strip(),
                middlename=self.entries['middlename'].get().strip(),
                phone=self.entries['phone'].get().strip(),
                email=self.entries['email'].get().strip(),
                position=self.entries['position'].get().strip(),
                role=UserRole.ADMIN,
                group_name="Библиотекари",
                course=0,
                department="Библиотека"
            )

            if self.db.users.register_user(librarian):
                messagebox.showinfo("Успех", "Библиотекарь успешно добавлен!")
                self.dialog.destroy()
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Ошибка",
                                     "Не удалось добавить библиотекаря! Возможно, такой логин уже существует.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

class EditLibrarianDialog:
    def __init__(self, parent, db, librarian_data, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать библиотекаря")
        self.dialog.geometry("400x500")
        self.db = db
        self.librarian_id = librarian_data['id']
        self.callback = callback
        self.frame = ttk.Frame(self.dialog, padding="20")
        self.frame.pack(fill="both", expand=True)
        self.entries = {}
        self._create_fields(librarian_data)

        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Сохранить", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)



    def _create_entry_field(self, label_text, field_name, show=None, initial_value=''):
        """Создает поле ввода с меткой и начальным значением."""
        ttk.Label(self.frame, text=label_text).pack(pady=(10, 0))
        entry = ttk.Entry(self.frame, show=show)
        entry.insert(0, initial_value)
        entry.pack(fill='x', pady=(0, 5))
        self.entries[field_name] = entry

    def _create_fields(self, librarian_data):
        """Создает поля с предзаполнением."""
        fields = [
            ('password', 'Новый пароль (оставьте пустым, если не меняется)', "*", ''),
            ('lastname', 'Фамилия', None, librarian_data.get('lastname', '')),
            ('firstname', 'Имя', None, librarian_data.get('firstname', '')),
            ('middlename', 'Отчество', None, librarian_data.get('middlename', '')),
            ('phone', 'Телефон', None, librarian_data.get('phone', '')),
            ('email', 'Email', None, librarian_data.get('email', '')),
            ('position', 'Должность', None, librarian_data.get('position', ''))
        ]
        for field_name, label_text, show_char, initial_value in fields:
            self._create_entry_field