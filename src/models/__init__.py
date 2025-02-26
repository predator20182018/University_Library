from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"

@dataclass
class User:
    username: str
    password: str
    lastname: str
    firstname: str
    middlename: str
    phone: str
    email: str
    group_name: str
    course: int
    position: str
    department: str
    role: UserRole = UserRole.USER
    id: int = None

@dataclass
class Book:
    title: str
    author: str
    status: str = "доступна"  # доступна, забронирована, выдана
    shelf_id: int = 1
    room_id: int = 1
    id: int = None
    borrower_id: int = None
    borrow_date: datetime = None
    return_date: datetime = None
    publisher_id: Optional[int] = None # Добавлено и тут

@dataclass
class Publisher:
    id: int
    name: str

@dataclass
class LoanJournal:
    id: int
    librarian_id: int
    reader_id: int
    book_id: int
    shelf_id: int
    room_id: int
    loan_date: datetime

@dataclass
class ReturnJournal:
    id: int
    loan_id: int
    librarian_id: int
    reader_id: int
    book_id: int
    shelf_id: int
    room_id: int
    return_date: datetime
    overdue_days: int

@dataclass
class ReservationJournal:
    id: int
    book_id: int
    shelf_id: int
    room_id: int
    reader_id: int
    reservation_date: datetime
    reservation_period: int
    notification_sent: bool
    notification_date: datetime = None