from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Book:
    """Модель книги в библиотеке"""
    title: str
    author: str
    status: str = "доступна"  # доступна, забронирована, выдана
    id: Optional[int] = None
    shelf_id: int = 1
    room_id: int = 1
    borrower_id: Optional[int] = None
    borrow_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    publisher_id: Optional[int] = None