from sqlalchemy.orm import Session
from repositories.user_repository.user_repository import UserRepository
from models.user.user import User


def test_get_user_by_email(db_session: Session):
    """Test retrieving a user by id."""
    # First, create a user in the database
    email = 'test2@email.com'
    password = '123'
    user = User(email, password)
    db_session.add(user)
    db_session.commit()

    assert user.email == email
    # Now, retrieve the user by email
    saved_user = UserRepository.get_by_email(db_session, user.email)
    assert saved_user is not None
    assert saved_user.email == email


def test_get_user_by_id(db_session: Session):
    """Test retrieving a user by id."""
    # First, create a user in the database
    email = 'test3@email.com'
    password = '123'
    user = User(email,password)
    db_session.add(user)
    db_session.commit()

    assert user.email == email
    # Now, retrieve the user by email
    saved_user = UserRepository.get_by_id(db_session, user.id)
    assert user is not None
    assert str(user.id) == str(saved_user.id)
    assert user.email == saved_user.email
