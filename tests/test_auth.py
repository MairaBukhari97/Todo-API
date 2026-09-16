def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"

def test_register_duplicate_username(client, registered_user):
    response = client.post("/auth/register", json={
        "username": registered_user["username"],
        "password": "different_password"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success(client, registered_user):
    response = client.post("/auth/login", data={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", data={
        "username": registered_user["username"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={
        "username": "nobody",
        "password": "password123"
    })
    assert response.status_code == 401