from .users import UserManager
from .books import BookManager
from .journals import JournalManager
import sqlite3

class Database:
    def __init__(self, db_name: str = 'library.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)  # Connect once
        self.conn.row_factory = sqlite3.Row # Для удобства работы с результатом
        self.users = UserManager(self)
        self.books = BookManager(self)
        self.journals = JournalManager(self)

        # Initialize database
        self.users.create_tables()
        self.books.create_tables()
        self.journals.create_tables()

        # Create initial data
        self.users.create_admin()
        self.books.create_publishers()

    def begin_transaction(self):
        self.conn.execute("BEGIN")

    def commit_transaction(self):
        self.conn.commit()

    def rollback_transaction(self):
        self.conn.rollback()

    def execute_query(self, query, params=None, fetchone=False, fetchall=False):
        """Вспомогательный метод для выполнения запросов"""
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
            else: #Для INSERT, UPDATE, DELETE
                return cursor.lastrowid #Вернет ID последней вставленной строки

        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            raise
        finally:
            cursor.close()