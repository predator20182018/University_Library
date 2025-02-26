import sqlite3
from typing import List

class JournalManager:
    def __init__(self, db):
        self.db = db

    def create_tables(self):
        try:
            self.db.begin_transaction()
            self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS loan_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    librarian_id INTEGER NOT NULL,
                    reader_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    shelf_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    loan_date TEXT NOT NULL,
                    FOREIGN KEY(librarian_id) REFERENCES users(id),
                    FOREIGN KEY(reader_id) REFERENCES users(id),
                    FOREIGN KEY(book_id) REFERENCES books(id)
                )
            ''')

            self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS return_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loan_id INTEGER NOT NULL,
                    librarian_id INTEGER NOT NULL,
                    reader_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    shelf_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    return_date TEXT NOT NULL,
                    overdue_days INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(loan_id) REFERENCES loan_journal(id),
                    FOREIGN KEY(librarian_id) REFERENCES users(id),
                    FOREIGN KEY(reader_id) REFERENCES users(id),
                    FOREIGN KEY(book_id) REFERENCES books(id)
                )
            ''')
            self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS reservation_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    shelf_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    reader_id INTEGER NOT NULL,
                    reservation_date TEXT NOT NULL,
                    reservation_period INTEGER NOT NULL,
                    notification_sent BOOLEAN NOT NULL DEFAULT 0,
                    notification_date TEXT,
                    FOREIGN KEY(book_id) REFERENCES books(id),
                    FOREIGN KEY(reader_id) REFERENCES users(id)
                )
            ''')
            self.db.commit_transaction()
        except sqlite3.Error:
            self.db.rollback_transaction()
            raise


    def _clear_journal(self, journal_name: str) -> bool:
        """Общий метод для очистки журналов."""
        try:
            self.db.begin_transaction()
            self.db.execute_query(f"DELETE FROM {journal_name}")
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False


    def clear_loan_journal(self) -> bool:
        return self._clear_journal("loan_journal")

    def clear_return_journal(self) -> bool:
        return self._clear_journal("return_journal")

    def clear_reservation_journal(self) -> bool:
        return self._clear_journal("reservation_journal")

    def add_loan(self, librarian_id: int, reader_id: int, book_id: int,
                shelf_id: int, room_id: int, loan_date: str) -> bool:
        try:
            self.db.begin_transaction()
            self.db.execute_query('''
                INSERT INTO loan_journal (
                    librarian_id, reader_id, book_id,
                    shelf_id, room_id, loan_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (librarian_id, reader_id, book_id, shelf_id, room_id, loan_date))
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False

    def add_return(self, loan_id: int, librarian_id: int, reader_id: int,
                  book_id: int, shelf_id: int, room_id: int,
                  return_date: str, overdue_days: int = 0) -> bool:

        try:
            self.db.begin_transaction()
            self.db.execute_query('''
                INSERT INTO return_journal (
                    loan_id, librarian_id, reader_id, book_id,
                    shelf_id, room_id, return_date, overdue_days
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (loan_id, librarian_id, reader_id, book_id,
                    shelf_id, room_id, return_date, overdue_days))
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False

    def add_reservation(self, book_id: int, shelf_id: int, room_id: int,
                       reader_id: int, reservation_date: str,
                       reservation_period: int) -> bool:
        try:
            self.db.begin_transaction()
            self.db.execute_query('''
                INSERT INTO reservation_journal (
                    book_id, shelf_id, room_id, reader_id,
                    reservation_date, reservation_period
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (book_id, shelf_id, room_id, reader_id,
                    reservation_date, reservation_period))
            self.db.commit_transaction()
            return True
        except sqlite3.Error:
            self.db.rollback_transaction()
            return False


    def get_loans(self) -> List[sqlite3.Row]:
        return self.db.execute_query('''
            SELECT * FROM loan_journal
            ORDER BY loan_date DESC
        ''', fetchall=True)

    def get_returns(self) -> List[sqlite3.Row]:
        return self.db.execute_query('''
            SELECT * FROM return_journal
            ORDER BY return_date DESC
        ''', fetchall=True)

    def get_reservations(self) -> List[sqlite3.Row]:
        return self.db.execute_query('''
                SELECT * FROM reservation_journal
                ORDER BY reservation_date DESC
            ''', fetchall=True)

    def get_user_loans(self, user_id: int) -> List[sqlite3.Row]:
        return self.db.execute_query('''
            SELECT * FROM loan_journal
            WHERE reader_id = ?
            ORDER BY loan_date DESC
        ''', (user_id,), fetchall=True)

    def get_user_reservations(self, user_id: int) -> List[sqlite3.Row]:
        return self.db.execute_query('''
            SELECT * FROM reservation_journal
            WHERE reader_id = ?
            ORDER BY reservation_date DESC
        ''', (user_id,), fetchall=True)