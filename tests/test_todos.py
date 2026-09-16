def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

# test_create_todo

def test_create_todo(client, auth_token):
    response = client.post("/todos", json={
        "title": "Test Todo",
        "description": "This is a test todo"
    }, headers = auth_headers(auth_token))
    assert response.status_code == 200
    assert response.json()["title"] == "Test Todo"

def test_create_todo_unauthorized(client):
    response = client.post("/todos", json={
        "title": "Unauthorized Todo",
        "description": "This should not be created"
    })
    assert response.status_code == 401


#  test_get_todos

def test_get_todos(client, auth_token):
    response = client.get("/todos", headers = auth_headers(auth_token))
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_todos_unauthorized(client):
    response = client.get("/todos")
    assert response.status_code == 401


#  test_get_todos_by_id

def test_get_todo_by_id(client, auth_token):
    create_response = client.post("/todos", json={
        "title": "Test Todo",
        "description": "This is a test todo"
    }, headers=auth_headers(auth_token))
    todo_id = create_response.json()["id"]
    # get the todo by ID
    response = client.get(f"/todos/{todo_id}", headers=auth_headers(auth_token))
    assert response.status_code == 200
    assert response.json()["id"] == todo_id

def test_get_todo_not_found(client, auth_token):
    response = client.get("/todos/999", headers=auth_headers(auth_token))
    assert response.status_code == 404

def test_get_todo_unauthorized(client):
    response = client.get("/todos/1")
    assert response.status_code == 401


# Update the todo

def test_update_todo(client, auth_token):
    create_response = client.post("/todos", json={
        "title": "Test Todo",
        "description": "This is a test todo"
    }, headers= auth_headers(auth_token))
    todo_id = create_response.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={
        "title": "Updated Todo",
        "description": "This is an updated todo"
    }, headers=auth_headers(auth_token))
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Todo"

def test_update_todo_not_found(client, auth_token):
    response = client.put("/todos/999", json={
        "title": "Updated Todo",
        "description": "This is an updated todo"
    }, headers=auth_headers(auth_token))
    assert response.status_code == 404

def test_update_todo_unauthorized(client):
    response = client.put("/todos/1", json={
        "title": "Updated Todo",
        "description": "This is an updated todo"
    })
    assert response.status_code == 401


#  test_delete_todo

def test_delete_todo(client, auth_token):
    # Create a todo
    create_response = client.post("/todos", json={
        "title": "Test Todo",
        "description": "This is a test todo"
    }, headers = auth_headers(auth_token))
    todo_id = create_response.json()["id"]
    # Delete the todo
    response = client.delete(f"/todos/{todo_id}", headers=auth_headers(auth_token))
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]

def test_delete_todo_not_found(client, auth_token):
    response = client.delete("/todos/999", headers=auth_headers(auth_token))
    assert response.status_code == 404

def test_delete_todo_unauthorized(client):
    response = client.delete("/todos/1")
    assert response.status_code == 401