# Todo API

A production-style REST API for managing todos, built with **FastAPI** and **PostgreSQL**. It includes JWT authentication, password hashing, request validation, rate limiting, and an automated test suite. It is deployed live on Railway.

**Live API docs:** `https://your-railway-url.up.railway.app/docs`

---

## Features

- **Full CRUD** for todos (create, read, update, delete)
- **Per-user data isolation**: each todo belongs to the user who created it, and users can only see and modify their own todos
- **JWT authentication** with register and login endpoints
- **Password hashing** with bcrypt (plain-text passwords are never stored)
- **Request validation** with Pydantic, with clear 422 errors on bad input
- **PostgreSQL** database accessed through the SQLAlchemy ORM
- **Rate limiting** on endpoints to protect against brute-force attacks
- **CORS** support so a frontend can connect
- **18 automated tests** with pytest, run against an isolated test database
- **Auto-generated interactive docs** (Swagger UI) at `/docs`
- **Secrets kept out of the repo** via environment variables

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Database | PostgreSQL (SQLite for tests) |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Authentication | JWT (python-jose), bcrypt (passlib) |
| Rate limiting | slowapi |
| Testing | pytest, httpx |
| Deployment | Railway + GitHub |

---

## Project Structure

```
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
├── requirements.txt
├── Procfile            # Railway start command
├── .env                # Local secrets (not committed)
└── .gitignore
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create a new user | No |
| POST | `/auth/login` | Log in and receive a JWT | No |

### Todos

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| GET | `/todos` | Get all of your todos | Yes |
| GET | `/todos/{id}` | Get one of your todos by ID | Yes |
| POST | `/todos` | Create a todo | Yes |
| PUT | `/todos/{id}` | Update a todo | Yes |
| DELETE | `/todos/{id}` | Delete a todo | Yes |

Protected endpoints expect the token in the request header:

```
Authorization: Bearer <your_token>
```

### Example requests

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

**Create a todo**
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

### Status codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (for example, username already taken) |
| 401 | Missing, invalid, or expired token, or wrong credentials |
| 404 | Todo not found (or it belongs to another user) |
| 422 | Validation error (request body has the wrong shape or types) |
| 429 | Rate limit exceeded |

---

## Getting Started

### Prerequisites

- Python 3.11+
- A PostgreSQL database (local, or a free one on Railway)

### 1. Clone the repository

```bash
git clone https://github.com/MairaBukhari97/todo-api.git
cd todo-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
```

Generate a strong secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive docs are at `http://127.0.0.1:8000/docs`.

---

## Running Tests

```bash
pytest tests/ -v
```

The suite has 18 tests: 5 for authentication and 13 for todos. Every todo endpoint is covered for the success case, the not-found case, and the unauthorized case.

Tests run against a separate SQLite database. The real database is swapped out using FastAPI's `dependency_overrides`, so your data is never touched.

---

## How It Works

### Authentication flow

1. A user registers. The password is hashed with bcrypt and stored as `hashed_password`.
2. The user logs in. The submitted password is checked against the stored hash.
3. On success, the server issues a JWT containing the username and a 30-minute expiry, signed with `SECRET_KEY`.
4. The client sends the token in the `Authorization` header with every request.
5. A `get_current_user` dependency verifies the token and loads the user before any protected endpoint runs. Failure returns `401`.

### Data ownership

Every `Todo` row has a `user_id` foreign key. When a todo is created, `user_id` is set from the authenticated user. Every read, update, and delete query filters by both the todo `id` and `current_user.id`, so one user can never access another user's todos. Requesting someone else's todo returns `404`.

### Request lifecycle (`POST /todos`)

1. FastAPI receives the request.
2. Pydantic validates the request body.
3. `get_current_user` verifies the JWT.
4. `get_db` opens a database session.
5. The endpoint creates the todo with the current user's ID, then runs `db.add()`, `db.commit()`, and `db.refresh()`.
6. The response is serialized through the `TodoOut` response model.
7. The session is closed in a `finally` block, so connections never leak.

---

## Deployment

The app is deployed on **Railway**:

1. Push the code to GitHub.
2. Create a Railway project from the GitHub repo.
3. Add a PostgreSQL service in the same project.
4. Set the `SECRET_KEY` and `DATABASE_URL` variables on the API service.
5. Railway installs `requirements.txt` and starts the app using the `Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Every push to the main branch triggers an automatic redeploy.

---

## Security Notes

- Passwords are hashed with bcrypt and never stored in plain text.
- `SECRET_KEY` and `DATABASE_URL` live in environment variables. `.env` is listed in `.gitignore`.
- Auth endpoints have stricter rate limits than normal endpoints to slow down brute-force attempts.
- For production, set `allow_origins` in the CORS config to your exact frontend domains instead of `"*"`.

---

## Future Improvements

- Add a `PATCH` endpoint for partial updates
- Add pagination and filtering to `GET /todos`
- Use Alembic for database migrations
- Add refresh tokens
- Build a React frontend

---

## Author

**Maira**
GitHub: [@MairaBukhari97](https://github.com/MairaBukhari97)