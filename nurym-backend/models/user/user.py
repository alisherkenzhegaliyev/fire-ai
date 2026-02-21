import uuid
import bcrypt
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(
        timezone.utc), nullable=False)

    def __init__(self, email: String, password: String):
        self.id = str(uuid.uuid4())
        self.email = email
        self.hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.is_deleted = False
        self.is_archived = False

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())

    def with_email(self, email):
        self.email = email
        return self

    def archive(self):
        self.is_archived = True
        return self

    def delete(self):
        self.is_deleted = True
        return self
