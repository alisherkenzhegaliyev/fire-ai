from models.user.user import User


def test_create_user():
    email = "test@email.com"
    password = "test@email.com"
    user = User(email, password)

    assert user.id is not None
    assert user.is_deleted is False
    assert user.is_archived is False


def test_delete_user():
    email = "test@email.com"
    password = "test@email.com"
    user = User(email, password)

    assert user.is_deleted is False

    user.delete()

    assert user.is_deleted is True


def test_archive_user():
    email = "test@email.com"
    password = "test@email.com"
    user = User(email, password)

    assert user.is_archived is False

    user.archive()

    assert user.is_archived is True


def test_update_user_email():
    email = "test@email.com"
    new_email = "new_test@email.com"
    password = "test@email.com"
    user = User(email, password)

    assert user.email == email

    user.with_email(new_email)

    assert user.email == new_email
