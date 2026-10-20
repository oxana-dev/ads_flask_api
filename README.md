# Flask Ads API

A RESTful API built with Flask for managing classified ads, with user authentication via JWT. Users can register, log in, and create, update, or delete their own ads, while anyone can browse the ads.

## Features

- User registration and login with hashed passwords
- JWT-based authentication (1-hour access tokens)
- Public read access to ads
- Authenticated users can create ads
- Only ad owners can update or delete their ads
- SQLite database by default (configurable via environment variables)

## Tech Stack

- **Flask** 3.0.3
- **Flask-SQLAlchemy** 3.1.1
- **Flask-JWT-Extended** 4.6.0
- **SQLAlchemy** 2.1.5
- **Werkzeug** (password hashing)
- **python-dotenv** (environment configuration)

## Project Structure
```
├── app/
│ ├── init.py # Application factory
│ ├── config.py # Configuration classes
│ ├── extensions.py # db, jwt instances
│ ├── models.py # User and Ad models
│ ├── auth/
│ │ └── routes.py # /auth endpoints
│ └── ads/
│ └── routes.py # /ads endpoints
├── init_db.py # Database initialization script
├── run.py # Application entry point
├── requirements.txt
└── env.example
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Clone the repository and navigate into it:

   ```bash
   git clone <your-repo-url>
   cd flask-ads-api
   ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
   
3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Copy the example environment file and adjust values:

    ```bash
    cp env.example .env
    ```

5. Edit .env and set strong values for SECRET_KEY and JWT_SECRET_KEY.


### Environment Variables

| Variable          | Description                          | Default              |
| ----------------- | ------------------------------------ | -------------------- |
| `SECRET_KEY`      | Flask secret key                     | `dev-secret`         |
| `JWT_SECRET_KEY`  | Secret used to sign JWT tokens       | `dev-jwt-secret`     |
| `DATABASE_URL`    | SQLAlchemy database URI              | `sqlite:///ads.db`   |

> **Note:** Never use the default secrets in production.

### Initialize the Database

Tables are created automatically when the app starts, but you can also run:

```bash
python init_db.py
```
This prints the list of created tables.

### Run the Application

```bash
python run.py
```

## API Endpoints

### Root

| Method | Endpoint | Description                    |
| ------ | -------- | ------------------------------ |
| GET    | `/`      | API info and endpoint listing  |

### Authentication

| Method | Endpoint         | Description           | Auth Required |
| ------ | ---------------- | --------------------- | ------------- |
| POST   | `/auth/register` | Register a new user   | No            |
| POST   | `/auth/login`    | Log in and get token  | No            |

**Register request body:**

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

**Login request body:**

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

**Login response:**

```json
{
  "access_token": "<jwt-token>"
}
```

### Ads

| Method | Endpoint       | Description               | Auth Required | Owner Only |
| ------ | -------------- | ------------------------- | ------------- | ---------- |
| GET    | `/ads/`        | List all ads              | No            | No         |
| GET    | `/ads/<id>`    | Get a single ad           | No            | No         |
| POST   | `/ads/`        | Create a new ad           | Yes           | —          |
| PATCH  | `/ads/<id>`    | Update an ad              | Yes           | Yes        |
| DELETE | `/ads/<id>`    | Delete an ad              | Yes           | Yes        |

**Create ad request body:**

```json
{
  "title": "Bicycle for sale",
  "description": "Almost new, 21-speed mountain bike."
}
```

**Create ad request body:**

```json
{
  "title": "Bicycle for sale",
  "description": "Almost new, 21-speed mountain bike."
}
```

**Ad response:**

```json
{
  "id": 1,
  "title": "Bicycle for sale",
  "description": "Almost new, 21-speed mountain bike.",
  "created_at": "2025-01-01T12:00:00+00:00",
  "owner_id": 1
}
```
### Authentication Header

For protected endpoints, include the JWT in the `Authorization` header:

Authorization: Bearer <access_token>

## Example Usage

```bash
# Register
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'

# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}' | jq -r .access_token)

# Create an ad
curl -X POST http://127.0.0.1:5000/ads/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Bicycle for sale","description":"Almost new."}'

# List ads
curl http://127.0.0.1:5000/ads/
```

## Error Handling

The API returns JSON errors with appropriate HTTP status codes:

| Status | Meaning                                       |
| ------ | --------------------------------------------- |
| 400    | Bad request (validation errors)               |
| 401    | Unauthorized (invalid credentials / token)    |
| 403    | Forbidden (not the owner of the ad)           |
| 404    | Resource not found                            |
| 409    | Conflict (email already registered)           |
| 422    | Unprocessable entity                          |

Example error response:

```json
{
  "error": "Ad not found"
}
```

## Running Tests

The project includes `pytest` and `pytest-flask`, with a test suite covering authentication and ad ownership rules.

### Test Configuration

Tests use an in-memory SQLite database and a separate `TestConfig` (defined in `tests/test_ads_api.py`), so they never touch your development or production data.

A `pytest.ini` file in the project root ensures the `app` package is importable when running pytest:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

## Notes for Production

- Replace SQLite with a production-grade database (PostgreSQL, MySQL, etc.) and use **Flask-Migrate** for schema migrations instead of `db.create_all()`.
- Set strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`.
- Disable `debug=True` in `run.py`.
- Serve the app behind a WSGI server such as Gunicorn or uWSGI, ideally behind a reverse proxy (Nginx).
- Consider adding token revocation, refresh tokens, and rate limiting.

## License

This project is provided as-is for educational purposes. Add your preferred license here.




