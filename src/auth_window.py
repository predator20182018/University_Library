import tkinter as tk
from tkinter import ttk, messagebox
import re
from .models import User, UserRole


class AuthWindow:
    def __init__(self, db, switch_to_main):
        self.db = db
        self.switch_to_main = switch_to_main
        self.root = None
        self.current_user_role = None

    def validate_name(self, value):
        return bool(re.match(r'^[а-яА-ЯёЁa-zA-Z-]*$', value))

    def validate_phone(self, value):
        return bool(re.match(r'^[0-9-]*$', value))

    def validate_course(self, value):
        if not value:
            return True
        try:
            num = int(value)
            return 0 <= num <= 10
        except ValueError:
            return False

    def validate_login(self, value):  # Добавлена валидация логина
        return bool(re.match(r'^[a-zA-Z0-9]*$', value))

    def register_callback(self, field_type):
        if field_type == "name":
            return (self.root.register(self.validate_name), '%P')
        elif field_type == "phone":
            return (self.root.register(self.validate_phone), '%P')
        elif field_type == "course":
            return (self.root.register(self.validate_course), '%P')
        elif field_type == "login":  # Добавлена валидация
            return (self.root.register(self.validate_login), '%P')
        return None  # Важно для других полей

    def show_login_window(self, root):
        self.root = root
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("325x300")

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(main_frame, text="Библиотека университета",
                  font=('Helvetica', 16, 'bold')).pack(pady=(0, 10))

        ttk.Label(main_frame, text="Вход",
                  font=('Helvetica', 12)).pack(pady=(0, 20))

        ttk.Label(main_frame, text="Логин:").pack(pady=(0, 5))
        username_entry = ttk.Entry(main_frame, width=30, validate="key",  # Добавлена валидация
                                  validatecommand=self.register_callback("login"))
        username_entry.pack(pady=(0, 10))

        ttk.Label(main_frame, text="Пароль:").pack(pady=(0, 5))
        password_entry = ttk.Entry(main_frame, show="*", width=30)
        password_entry.pack(pady=(0, 20))

        ttk.Button(main_frame, text="Войти",
                   command=lambda: self.login(username_entry.get(), password_entry.get())
                   ).pack(pady=(0, 10))

        ttk.Button(main_frame, text="Регистрация",
                   command=self.show_registration_window).pack()

    def login(self, username, password):
        if not username.strip() or not password.strip():
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
            return

        success, role, user = self.db.users.verify_login(username, password)
        if success:
            self.current_user_role = role
            self.switch_to_main(role, user)
        else:
            messagebox.showerror("Ошибка", "Неверные учетные данные!")

    def show_registration_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("250x520")

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        ttk.Label(scrollable_frame, text="Регистрация",
                  font=('Helvetica', 16, 'bold')).pack(pady=(0, 20))

        fields = {}
        field_labels = {
            'username': 'Логин',
            'password': 'Пароль',
            'lastname': 'Фамилия',
            'firstname': 'Имя',
            'middlename': 'Отчество',
            'phone': 'Телефон',
            'email': 'Email',
            'group_name': 'Группа',
            'course': 'Курс',
            'position': 'Должность',
            'department': 'Кафедра'
        }

        for field, label in field_labels.items():
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill='x', pady=5)

            ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT)

            if field == 'password':
                entry = ttk.Entry(frame, show="*")
            elif field in ['lastname', 'firstname', 'middlename']:
                entry = ttk.Entry(frame, validate="key",
                                  validatecommand=self.register_callback("name"))
            elif field == 'phone':
                entry = ttk.Entry(frame, validate="key",
                                  validatecommand=self.register_callback("phone"))
            elif field == 'course':
                entry = ttk.Entry(frame, validate="key",
                                  validatecommand=self.register_callback("course"))

            elif field == 'username': # Валидация для логина
                entry = ttk.Entry(frame, validate="key",
                                      validatecommand=self.register_callback("login"))
            else:
                entry = ttk.Entry(frame)

            entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(10, 0))
            fields[field] = entry

        ttk.Button(scrollable_frame, text="Зарегистрироваться",
                   command=lambda: self.register_user(fields)).pack(pady=20)

        ttk.Button(scrollable_frame, text="Назад",
                   command=lambda: self.show_login_window(self.root)).pack()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def register_user(self, fields):
        try:
            for field_name, field in fields.items():
                if not field.get().strip():
                    raise ValueError(f"Поле '{field_name}' обязательно для заполнения")

            user = User(
                username=fields['username'].get().strip(),
                password=fields['password'].get().strip(),
                lastname=fields['lastname'].get().strip(),
                firstname=fields['firstname'].get().strip(),
                middlename=fields['middlename'].get().strip(),
                phone=fields['phone'].get().strip(),
                email=fields['email'].get().strip(),
                group_name=fields['group_name'].get().strip(),
                course=int(fields['course'].get().strip()),
                position=fields['position'].get().strip(),
                department=fields['department'].get().strip(),
                role=UserRole.USER
            )

            if self.db.users.register_user(user):
                messagebox.showinfo("Успех", "Регистрация успешно завершена!")
                self.show_login_window(self.root)
            else:
                messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует!")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))