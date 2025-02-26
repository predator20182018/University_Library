import sqlite3
import bcrypt
from typing import Optional, Tuple, List
from ..models import User, UserRole


class UserManager:
    def __init__(self, db):
        self.db = db

    def create_tables(self):
        try:
            self.db.begin_transaction()
            self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    firstname TEXT NOT NULL,
                    middlename TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    group_name TEXT NOT NULL,
                    course INTEGER,
                    position TEXT,
                    department TEXT,
                    role TEXT NOT NULL DEFAULT 'user'
                )
            ''')
            self.db.commit_transaction()
        except sqlite3.Error:
            self.db.rollback_transaction()
            raise

    @staticmethod
    def hash_password(password: str) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def verify_password(password: str, password_hash: bytes) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)

    def create_admin(self):
        admin_user = User(
            username="admin",
            password="admin123",
            lastname="Admin",
            firstname="Admin",
            middlename="Admin",
            phone="+71234567890",
            email="admin@library.com",
            group_name="Administrators",
            course=0,
            position="Administrator",
            department="Library",
            role=UserRole.ADMIN
        )

        owner_user = User(
            username="owner",
            password="owner123",
            lastname="Owner",
            firstname="Owner",
            middlename="Owner",
            phone="+71234567891",
            email="owner@library.com",
            group_name="Administrators",
            course=0,
            position="Library Owner",
            department="Library",
            role=UserRole.OWNER
        )
        try:
            self.db.begin_transaction()
            for user in [admin_user, owner_user]:
                self.register_user(user)
            self.db.commit_transaction()
        except sqlite3.Error:
            self.db.rollback_transaction()
            raise

    def register_user(self, user: User) -> bool:
        try:
            password_hash = self.hash_password(user.password)
            self.db.execute_query('''
                INSERT OR IGNORE INTO users (
                    username, password_hash, lastname, firstname, middlename,
                    phone, email, group_name, course, position, department, role
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.username,
                password_hash,
                user.lastname,
                user.firstname,
                user.middlename,
                user.phone,
                user.email,
                user.group_name,
                user.course,
                user.position,
                user.department,
                user.role.value
            ))

            return True  # Возвращаем True, если вставка прошла успешно
        except sqlite3.IntegrityError:
            return False  # Возвращаем False, если пользователь с таким именем уже существует
        except sqlite3.Error:
            return False # Другие ошибки

    def update_librarian(self, user_id: int, user_data: dict) -> bool:
        try:
            self.db.begin_transaction()
            update_fields = []
            params = []

            # Формируем список полей для обновления
            for field in ['lastname', 'firstname', 'middlename', 'phone',
                            'email', 'position']:
                if field in user_data:
                    update_fields.append(f"{field} = ?")
                    params.append(user_data[field])

            # Если указан новый пароль, хешируем его
            if 'password' in user_data and user_data['password']:
                update_fields.append("password_hash = ?")
                params.append(self.hash_password(user_data['password']))

            # Добавляем id в параметры
            params.append(user_id)

            # Формируем и выполняем запрос
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            self.db.execute_query(query, params)
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False

    def delete_librarian(self, user_id: int) -> bool:
        try:
            self.db.begin_transaction()
            # Проверяем, что удаляемый пользователь - библиотекарь
            result = self.db.execute_query("SELECT role FROM users WHERE id = ?", (user_id,), fetchone=True)

            if not result or result['role'] != UserRole.ADMIN.value:
                self.db.rollback_transaction()
                return False

            self.db.execute_query("DELETE FROM users WHERE id = ?", (user_id,))
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False

    def verify_login(self, username: str, password: str) -> Tuple[bool, Optional[UserRole], Optional[User]]:
        result = self.db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                (username,), fetchone=True
            )
        if result and self.verify_password(password, result['password_hash']):  # index 2 is password_hash
            user = User(
                id=result['id'],
                username=result['username'],
                password="",  # Don't include password in returned user object
                lastname=result['lastname'],
                firstname=result['firstname'],
                middlename=result['middlename'],
                phone=result['phone'],
                email=result['email'],
                group_name=result['group_name'],
                course=result['course'],
                position=result['position'],
                department=result['department'],
                role=UserRole(result['role'])
            )
            return True, UserRole(result['role']), user

        return False, None, None

    def get_librarians(self) -> List[User]:

        rows = self.db.execute_query("""
            SELECT * FROM users WHERE role = ?
        """, (UserRole.ADMIN.value,), fetchall=True)

        librarians = []
        for row in rows:
            librarian = User(
                id=row['id'],
                username=row['username'],
                password="",  # Don't include password
                lastname=row['lastname'],
                firstname=row['firstname'],
                middlename=row['middlename'],
                phone=row['phone'],
                email=row['email'],
                group_name=row['group_name'],
                course=row['course'],
                position=row['position'],
                department=row['department'],
                role=UserRole(row['role'])
            )
            librarians.append(librarian)
        return librarians