# Todo API

A REST API for managing todos, built with **FastAPI** and **PostgreSQL**. It includes JWT authentication, password hashing, request validation, rate limiting, and an automated test suite.

The project demonstrates backend development concepts, including authentication, database management, API security, and automated testing.

---

## Features

* **Full CRUD** for todos (create, read, update, delete)
* **Per-user data isolation**: Each todo belongs to the user who created it, and users can only access and modify their own todos.
* **JWT authentication** with register and login endpoints.
* **Password hashing** with bcrypt (plain-text passwords are never stored).
* **Request validation** with Pydantic, with clear 422 errors on invalid input.
* **PostgreSQL** database accessed through the SQLAlchemy ORM.
* **Rate limiting** on endpoints to protect against brute-force attacks.
* **CORS** support so a frontend can connect.
* **18 automated tests** with pytest, running against an isolated SQLite test database.
* **Auto-generated interactive documentation** (Swagger UI) at `/docs`.
* **Environment variables** for managing sensitive configuration.

---

## Tech Stack

| Layer          | Technology                          |
| -------------- | ----------------------------------- |
| Framework      | FastAPI                             |
| Database       | PostgreSQL (SQLite for tests)       |
| ORM            | SQLAlchemy                          |
| Validation     | Pydantic                            |
| Authentication | JWT (python-jose), bcrypt (passlib) |
| Rate Limiting  | slowapi                             |
| Testing        | pytest, httpx                       |
| Language       | Python                              |

---

## Project Structure

```text
todo_api/
├── main.py             # API endpoints and dependencies
├── database.py         # Database engine, session factory, Base
├── models.py           # SQLAlchemy models (User, Todo)
├── auth.py             # Password hashing and JWT logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py     # Test database setup and fixtures
│   ├── test_auth.py    # Auth endpoint tests
│   └── test_todos.py   # Todo endpoint tests
├── requirements.txt    # Project dependencies
├── .env                # Local secrets (not committed)
└── .gitignore
```

---

## API Endpoints

### Authentication

| Method | Endpoint         | Description              | Auth Required |
| ------ | ---------------- | ------------------------ | ------------- |
| POST   | `/auth/register` | Create a new user        | No            |
| POST   | `/auth/login`    | Log in and receive a JWT | No            |

### Todos

| Method | Endpoint      | Description                 | Auth Required |
| ------ | ------------- | --------------------------- | ------------- |
| GET    | `/todos`      | Get all your todos          | Yes           |
| GET    | `/todos/{id}` | Get one of your todos by ID | Yes           |
| POST   | `/todos`      | Create a todo               | Yes           |
| PUT    | `/todos/{id}` | Update a todo               | Yes           |
| DELETE | `/todos/{id}` | Delete a todo               | Yes           |

Protected endpoints expect the token in the request header:

```text
Authorization: Bearer <your_token>
```

### Example Requests

**Register**

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "maira", "password": "strongpassword123"}'
```

**Login**

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=maira&password=strongpassword123"
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Create a Todo**

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "2 litres"}'
```

Response:

```json
{
  "id": 1,
  "title": "Buy milk",
  "description": "2 litres",
  "completed": false
}
```

### HTTP Status Codes

| Code | Meaning                                                      |
| ---- | ------------------------------------------------------------ |
| 200  | Success                                                      |
| 400  | Bad request (e.g., username already taken)                   |
| 401  | Missing, invalid, or expired token, or incorrect credentials |
| 404  | Todo not found or does not belong to the authenticated user  |
| 422  | Request validation error                                     |
| 429  | Rate limit exceeded                                          |

---

## Getting Started

### Prerequisites

* Python 3.11+
* PostgreSQL
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/MairaBukhari97/todo-api.git
cd todo-api
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
```

Generate a strong secret key using:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace the database URL with your actual PostgreSQL connection details.

### 5. Run the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

* **API:** http://127.0.0.1:8000
* **Swagger UI:** http://127.0.0.1:8000/docs
* **ReDoc:** http://127.0.0.1:8000/redoc

---

## Running Tests

Run the automated test suite using:

```bash
pytest tests/ -v
```

The test suite contains 18 tests:

* 5 authentication tests
* 13 todo endpoint tests

Tests run against a separate SQLite database. The application's database dependency is overridden using FastAPI's `dependency_overrides`, ensuring that tests do not affect the actual database.

---

## How It Works

### Authentication Flow

1. A user registers with a username and password.
2. The password is hashed using bcrypt and stored as `hashed_password`.
3. During login, the submitted password is checked against the stored hash.
4. On successful authentication, the server generates a JWT containing the username and a 30-minute expiry.
5. The client sends the token in the `Authorization` header with subsequent requests.
6. The `get_current_user` dependency verifies the token and retrieves the authenticated user.
7. Invalid or expired tokens result in a `401 Unauthorized` response.

### Data Ownership

Every `Todo` record has a `user_id` foreign key referencing its owner.

When a todo is created, its `user_id` is assigned using the currently authenticated user's ID.

All read, update, and delete operations filter records using both the todo ID and the authenticated user's ID.

This ensures that users cannot access or modify another user's todos.

### Request Lifecycle (POST /todos)

1. FastAPI receives the request.
2. Pydantic validates the request body.
3. `get_current_user` verifies the JWT.
4. `get_db` provides a database session.
5. The endpoint creates a todo associated with the authenticated user.
6. `db.add()`, `db.commit()`, and `db.refresh()` handle database operations.
7. The response is serialized using the `TodoOut` response model.
8. The database session is closed after the request.

---

## Security Notes

* Passwords are hashed using bcrypt and never stored in plain text.
* `SECRET_KEY` and `DATABASE_URL` are stored in environment variables.
* The `.env` file is included in `.gitignore` to prevent accidental exposure of secrets.
* Authentication endpoints have stricter rate limits to help prevent brute-force attacks.
* For production use, configure CORS to allow only trusted frontend domains instead of using `"*"`.

---

## Author

**Maira**

GitHub: [@MairaBukhari97](https://github.com/MairaBukhari97)
