"""
User repository for performing CRUD operations on the User model.

This module provides methods to save a new user, retrieve a user by their ID,
and retrieve a user by their email from the database.
"""
from sqlalchemy.orm import Session
from models.user.user import User

class UserRepository:
    """
    Repository class for handling CRUD operations on the User model.
    Provides methods for saving a user and retrieving users by their ID or email.
    """

    @staticmethod
    def get_by_id(session: Session, user_id: str) -> (User | None):
        """
        Retrieves a user from the database by their ID.

        Args:
            session (Session): The database session.
            id (str): The ID of the user to retrieve.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(session: Session, email: str) -> (User | None):
        """
        Retrieves a user from the database by their email address.

        Args:
            session (Session): The database session.
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        return session.query(User).filter(User.email == email).first()
