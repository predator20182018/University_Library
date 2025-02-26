from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class UserRole(Enum):
    USER = 'user'
    ADMIN = 'admin'
    OWNER = 'owner'

@dataclass
class User:
    """Модель пользователя системы"""
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
    id: Optional[int] = None
    birth_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Сериализация пользователя"""
        return {
            'id': self.id,
            'username': self.username,
            'lastname': self.lastname,
            'firstname': self.firstname,
            'middlename': self.middlename,
            'email': self.email,
            'phone': self.phone,
            'group_name': self.group_name,
            'course': self.course,
            'position': self.position,
            'department': self.department,
            'role': self.role.value,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None
        }