import sqlite3
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ..models import Book, Publisher
from ..search_engine import SearchType

MAX_BOOKS_PER_SHELF = 250
MAX_ROOMS = 3  # Максимальное количество помещений
MAX_SHELVES = 5  # Максимальное количество стеллажей


class BookManager:
    def __init__(self, db):
        self.db = db

    def create_tables(self):
        try:
            self.db.begin_transaction()
            self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'доступна',
                    shelf_id INTEGER NOT NULL DEFAULT 1,
                    room_id INTEGER NOT NULL DEFAULT 1,
                    borrower_id INTEGER,
                    borrow_date TEXT,
                    return_date TEXT,
                    publisher_id INTEGER,
                    FOREIGN KEY(borrower_id) REFERENCES users(id),
                    FOREIGN KEY(publisher_id) REFERENCES publishers(id)
                )
            ''')

            self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS publishers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            self.db.commit_transaction()
        except sqlite3.Error:
            self.db.rollback_transaction()
            raise


    def create_publishers(self):
        default_publishers = ["Эксмо", "АСТ", "Просвещение", "Дрофа", "Питер"]
        try:
            self.db.begin_transaction()
            for publisher in default_publishers:
                self.db.execute_query('INSERT OR IGNORE INTO publishers (name) VALUES (?)', (publisher,))
            self.db.commit_transaction()

        except sqlite3.Error:
            self.db.rollback_transaction()
            raise

    def count_books_in_shelf(self, room_id: int, shelf_id: int) -> int:
        result = self.db.execute_query("""
            SELECT COUNT(*) FROM books
            WHERE room_id = ? AND shelf_id = ?
        """, (room_id, shelf_id), fetchone=True)
        return result[0] if result else 0


    def get_books(self, search_term: str = "", room_id: Optional[int] = None,
                  shelf_id: Optional[int] = None, search_type: SearchType = SearchType.ALL) -> List[Book]:

        query = """SELECT id, title, author, status, shelf_id, room_id, borrower_id, borrow_date, return_date, publisher_id
                   FROM books WHERE 1=1"""  # Явно перечисляем колонки
        params = []

        if search_term:
            if search_type == SearchType.TITLE:
                query += " AND LOWER(title) LIKE LOWER(?)" #Изменено
                params.append(f"%{search_term}%")
            elif search_type == SearchType.AUTHOR:
                query += " AND LOWER(author) LIKE LOWER(?)" #Изменено
                params.append(f"%{search_term}%")


        if room_id is not None:
            query += " AND room_id = ?"
            params.append(room_id)

        if shelf_id is not None:
            query += " AND shelf_id = ?"
            params.append(shelf_id)

        rows = self.db.execute_query(query, params, fetchall=True)
        books = []

        for row in rows:
            book = Book(
                id=row['id'],
                title=row['title'],
                author=row['author'],
                status=row['status'],
                shelf_id=row['shelf_id'],
                room_id=row['room_id'],
                borrower_id=row['borrower_id'],
                borrow_date=datetime.fromisoformat(row['borrow_date']) if row['borrow_date'] else None,
                return_date=datetime.fromisoformat(row['return_date']) if row['return_date'] else None,
                publisher_id=row['publisher_id']
            )
            books.append(book)
        return books

    def add_book(self, title: str, author: str, shelf_id: int = 1, room_id: int = 1, publisher_id: Optional[int] = None) -> bool:
        if not (1 <= room_id <= MAX_ROOMS and 1 <= shelf_id <= MAX_SHELVES):  # Добавлена проверка
            return False
        if self.count_books_in_shelf(room_id, shelf_id) >= MAX_BOOKS_PER_SHELF:
            return False
        try:
            self.db.begin_transaction()
            self.db.execute_query(
                "INSERT INTO books (title, author, shelf_id, room_id, status, publisher_id) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, shelf_id, room_id, 'доступна', publisher_id)
            )
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False

    def edit_book(self, book_id: int, book_data: Dict) -> bool:
        if not (1 <= book_data['room_id'] <= MAX_ROOMS and 1 <= book_data['shelf_id'] <= MAX_SHELVES):  # Добавлена проверка
            return False

        try:
            self.db.begin_transaction()
            self.db.execute_query("""
                UPDATE books
                SET title = ?, author = ?, shelf_id = ?, room_id = ?,
                    status = ?, borrower_id = ?, borrow_date = ?, return_date = ?, publisher_id=?
                WHERE id = ?
            """, (
                book_data['title'],
                book_data['author'],
                book_data['shelf_id'],
                book_data['room_id'],
                book_data['status'],
                book_data.get('borrower_id'),
                datetime.now().isoformat() if book_data['status'] in ['забронирована', 'выдана'] else None,
                (datetime.now() + timedelta(days=14)).isoformat() if book_data['status'] in ['забронирована', 'выдана'] else None,
                book_data.get('publisher_id'),
                book_id
            ))
            self.db.commit_transaction()
            return True

        except sqlite3.Error:
            self.db.rollback_transaction()
            return False


    def delete_book(self, book_id: int) -> bool:
        try:
            self.db.begin_transaction()
            self.db.execute_query("DELETE FROM books WHERE id = ?", (book_id,))
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False

    def reserve_book(self, book_id: int, reader_id: int, shelf_id: int, room_id: int,
                     reservation_period: int = 14) -> bool:

        try:
            self.db.begin_transaction()
            result = self.db.execute_query("SELECT status FROM books WHERE id = ?", (book_id,), fetchone=True)
            if not result or result['status'] != 'доступна':
                self.db.rollback_transaction()  # Откат, если книга не найдена
                return False

            borrow_date = datetime.now()
            return_date = borrow_date + timedelta(days=reservation_period)

            self.db.execute_query("""
                UPDATE books
                SET status = 'забронирована', borrower_id = ?,
                    borrow_date = ?, return_date = ?
                WHERE id = ?
            """, (
                reader_id,
                borrow_date.isoformat(),
                return_date.isoformat(),
                book_id
            ))
            self.db.commit_transaction()
            return True

        except sqlite3.Error:
            self.db.rollback_transaction()
            return False

    def get_publishers(self) -> List[Publisher]:
        rows = self.db.execute_query("SELECT id, name FROM publishers", fetchall=True)
        return [Publisher(id=row['id'], name=row['name']) for row in rows]

    def get_publisher_id_by_name(self, publisher_name: str) -> Optional[int]:
        """Получает ID издательства по его названию."""
        row = self.db.execute_query("SELECT id FROM publishers WHERE name = ?", (publisher_name,), fetchone=True)
        return row['id'] if row else None

    def add_publisher(self, name: str) -> int:
        """Добавляет новое издательство и возвращает его ID.
            Если издательство уже существует, возвращает его ID."""
        try:
            self.db.begin_transaction()
            # Проверяем, существует ли уже издательство с таким именем
            existing_publisher_id = self.get_publisher_id_by_name(name)
            if existing_publisher_id:
                self.db.rollback_transaction()  # Откат, так как издательство уже есть
                return existing_publisher_id

            # Если издательства нет, добавляем его
            publisher_id = self.db.execute_query('INSERT INTO publishers (name) VALUES (?)', (name,),)
            self.db.commit_transaction()
            return publisher_id
        except sqlite3.Error:
            self.db.rollback_transaction()
            raise