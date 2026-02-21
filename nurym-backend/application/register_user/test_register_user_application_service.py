import uuid
from sqlalchemy.orm import Session
from facade import register_user
from application.register_user.register_user_application_service import UserRegistrationData
from models.user.user import User
import pytest

def test_execute_creates_user(db_session: Session):
    """
    Test that the execute function creates a new user in the database.
    """
    data = UserRegistrationData(
        email=f"{str(uuid.uuid4())}@test.com", password=str(uuid.uuid4()))
    new_user = register_user(data, db_session)

    # Assert that the correct user object was created
    assert new_user.email == data.email
    assert isinstance(new_user, User)

def test_execute_user_already_registered(db_session: Session):
    """
    Test that trying to register a user with an already existing email raises an error.
    """
    # Create a new user first
    email = f"{str(uuid.uuid4())}@test.com"
    password = str(uuid.uuid4())
    data = UserRegistrationData(email=email, password=password)
    register_user(data, db_session)  # First registration

    # Try to register again with the same email
    duplicate_data = UserRegistrationData(
        email=email, password=str(uuid.uuid4()))

    # Assert that it raises a ValueError when user is already registered
    with pytest.raises(ValueError, match="User already registered"):
        register_user(duplicate_data, db_session)
