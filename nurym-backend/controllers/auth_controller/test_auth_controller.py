from models.user.user import User

def test_sign_up_success(client):
    payload = {"email": "newuser@example.com", "password": "123123"}
    
    response = client.post("/auth/sign_up", json=payload)
    assert response.status_code == 201  # Status code 201 for successful creation


# Test sign_up failure (email already exists)
def test_sign_up_user_exists(client, db_session):
    payload = {"email": "testuser1@example.com", "password": "123123"}

    user = User(email="testuser1@example.com", password="Password123!")
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/sign_up", json=payload)
    assert response.status_code == 400
    assert response.json() == {'detail': 'User already registered'}


# Test sign_in success
def test_sign_in_success(client, db_session):
    user_payload = {"email": "testuser2@example.com", "password": "Password123!"}
    user = User(email="testuser2@example.com", password="Password123!")
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/sign_in", json=user_payload)
    assert response.status_code == 200
    response_json = response.json()
    assert "access_token" in response_json
    assert response_json["access_token"] != ""


# Test sign_in failure (incorrect password)
def test_sign_in_incorrect_password(client, db_session):
    user_payload = {"email": "testuser3@example.com", "password": "WrongPassword"}
    user = User(email="testuser3@example.com", password="123123")
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/sign_in", json=user_payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


# Test sign_in failure (user not found)
def test_sign_in_user_not_found(client):
    user_payload = {"email": "nonexistentuser@example.com", "password": "Password123!"}

    response = client.post("/auth/sign_in", json=user_payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}
