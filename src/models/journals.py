from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LoanJournal:
    """Журнал выдачи книг"""
    id: int
    librarian_id: int
    reader_id: int
    book_id: int
    shelf_id: int
    room_id: int
    loan_date: datetime

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'librarian_id': self.librarian_id,
            'reader_id': self.reader_id,
            'book_id': self.book_id,
            'shelf_id': self.shelf_id,
            'room_id': self.room_id,
            'loan_date': self.loan_date.isoformat()
        }

@dataclass
class ReturnJournal:
    """Журнал возврата книг"""
    id: int
    loan_id: int
    librarian_id: int
    reader_id: int
    book_id: int
    shelf_id: int
    room_id: int
    return_date: datetime
    overdue_days: int

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'librarian_id': self.librarian_id,
            'reader_id': self.reader_id,
            'book_id': self.book_id,
            'shelf_id': self.shelf_id,
            'room_id': self.room_id,
            'return_date': self.return_date.isoformat(),
            'overdue_days': self.overdue_days
        }

@dataclass
class ReservationJournal:
    """Журнал резервирования книг"""
    id: int
    book_id: int
    shelf_id: int
    room_id: int
    reader_id: int
    reservation_date: datetime
    reservation_period: int
    notification_sent: bool
    notification_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'book_id': self.book_id,
            'shelf_id': self.shelf_id,
            'room_id': self.room_id,
            'reader_id': self.reader_id,
            'reservation_date': self.reservation_date.isoformat(),
            'reservation_period': self.reservation_period,
            'notification_sent': self.notification_sent,
            'notification_date': self.notification_date.isoformat() if self.notification_date else None
        }