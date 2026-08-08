# User Management API

## Overview

A REST API for managing users, built with **Flask** and **MySQL**. It supports creating users, listing them with search and pagination, and fetching a single user by ID. The API is JSON-only (no server-rendered pages) and returns a consistent response shape for both success and error cases.

## Features

- Create and retrieve users
- Case-insensitive search by name or email
- Database-level pagination (no loading the whole table into memory)
- Input validation with clear, single-message error responses
- Duplicate email detection (409), enforced at both the application and database level
- Centralized JSON error handling - no HTML error pages, no leaked stack traces
- MySQL persistence via SQLAlchemy
- Modular, layered architecture (routes → validation → service → model)
- Automated tests (pytest) run against a real MySQL test database
- Optional React admin UI for visually exercising the API (see [Admin UI](#admin-ui-optional))

## Tech Stack

| Technology | Why |
|---|---|
| **Flask** | Lightweight, unopinionated web framework - a good fit for a small, API-first service. |
| **Flask-SQLAlchemy** | ORM on top of SQLAlchemy; gives us models, sessions, and database-level pagination without hand-writing SQL. |
| **PyMySQL** | Pure-Python MySQL driver - no native/C build step, so it installs cleanly across environments. |
| **MySQL** | The required relational database; enforces the UNIQUE email constraint at the storage layer. |
| **Marshmallow** | Declarative schema validation for the request body, with custom messages for each failure case. |
| **python-dotenv** | Loads configuration from a `.env` file so credentials never live in code. |
| **pytest** | Test runner, used with Flask's built-in test client. |

## Project Structure

```
user-management-api/
├── app/
│   ├── __init__.py          # create_app() application factory
│   ├── extensions.py        # shared SQLAlchemy instance
│   ├── errors.py            # custom exceptions + centralized JSON error handlers
│   ├── routes/
│   │   └── user_routes.py   # HTTP layer - parses requests, calls services
│   ├── models/
│   │   └── user.py          # SQLAlchemy User model (maps to the `users` table)
│   ├── services/
│   │   └── user_service.py  # business logic - search, pagination, duplicate handling
│   ├── schemas/
│   │   └── user_schema.py   # request validation (Marshmallow)
│   └── utils/
│       ├── responses.py     # standard {"success": .., "data": ..} envelope
│       └── pagination.py    # page/limit parsing and validation
├── tests/
│   ├── conftest.py          # pytest fixtures (Flask test client, MySQL test DB)
│   └── test_users.py        # endpoint tests (success + failure cases)
├── database/
│   └── init.sql             # creates the `users` database, table, and test database
├── frontend/                # optional React + Vite + Tailwind admin UI (see below)
├── .env.example              # documented environment variables (no real secrets)
├── config.py                  # environment-based Flask configuration
├── requirements.txt
├── run.py                     # application entry point
└── README.md
```

**Why routes/services/models are separated:** routes only parse the request and format the response; all business rules (duplicate checks, search, pagination) live in `services/`; the model only describes the table. This keeps each file small and means a route can be read top-to-bottom without wading through SQL or validation logic.

## Prerequisites

- Python 3.10+
- MySQL Server 8.0+ (a local install, or the provided Docker option)
- pip
- Git
- Node.js 18+ / npm - only needed for the optional [admin UI](#admin-ui-optional)

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your own local values - `.env` is git-ignored and must never be committed.

```bash
cp .env.example .env
```

| Variable | Purpose | Example |
|---|---|---|
| `FLASK_ENV` | Which config to load (`development`, `testing`, `production`) | `development` |
| `SECRET_KEY` | Flask session/signing secret | a long random string |
| `DATABASE_URL` | Main app database connection string | `mysql+pymysql://root:your_password@localhost:3306/users` |
| `TEST_DATABASE_URL` | Database used only by `pytest` - must be separate from `DATABASE_URL` | `mysql+pymysql://root:your_password@localhost:3306/users_test` |

## Database Setup

1. Make sure a MySQL server is reachable (locally installed, or run one in Docker: `docker run -d --name um_mysql -e MYSQL_ROOT_PASSWORD=yourpassword -p 3306:3306 mysql:8.0`).
2. Create the database and table using the provided script:
   ```bash
   mysql -u root -p < database/init.sql
   ```
   This creates the `users` database with the `users` table (including the `UNIQUE` constraint on `email`), plus a `users_test` database for the test suite.
3. Set `DATABASE_URL` (and `TEST_DATABASE_URL`) in `.env` to point at these databases with your credentials.

## Run Application

```bash
python run.py
```

The API is served at `http://127.0.0.1:5000`.

## Admin UI (Optional)

A small React + Vite + Tailwind dashboard lives in [`frontend/`](frontend/) for visually exercising the API - it's optional and not required by the assignment; the backend above is the actual deliverable. It calls the Flask API directly and doesn't duplicate any validation or business logic (e.g. the "Name is required" message you see in the create form is the exact string the API returned).

**Setup (once):**
```bash
cd frontend
npm install
cp .env.example .env   # points at http://127.0.0.1:5000 by default
```

**Run (with the Flask API already running separately):**
```bash
npm run dev
```
Open `http://localhost:5173`.

Because the UI runs on a different port than the API, the backend needs CORS enabled for it - see the `CORS_ORIGINS` variable in `.env` (already defaults to the Vite dev server's origin).

**What it shows:** total user count, a searchable/paginated user table, a "Create User" modal (with the API's own validation errors surfaced inline), loading skeletons, empty states, an error banner if the API is unreachable, a light/dark toggle, and a responsive layout down to mobile widths.

## API Documentation

All responses are JSON with a consistent envelope:

```json
{ "success": true, "data": ... }
{ "success": false, "error": "..." }
```

### GET /users

Retrieve users, with optional search and pagination.

- **Method:** `GET`
- **URL:** `/users`
- **Query parameters:**
  - `search` (optional) - matched case-insensitively against `name` and `email`
  - `page` (optional, default `1`)
  - `limit` (optional, default `10`, max `100`)

**Example:** `GET /users?search=saloni&page=1&limit=10`

**Success (200):**
```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "Saloni", "email": "saloni@example.com", "role": "Developer" }
  ],
  "pagination": { "page": 1, "limit": 10, "total": 1, "pages": 1 }
}
```

**Error - invalid pagination (400):**
```json
{ "success": false, "error": "Invalid pagination parameters" }
```

### POST /users

Create a new user.

- **Method:** `POST`
- **URL:** `/users`
- **Body:** `application/json`
  ```json
  { "name": "Saloni", "email": "saloni@example.com", "role": "Developer" }
  ```

**Success (201):**
```json
{
  "success": true,
  "data": { "id": 1, "name": "Saloni", "email": "saloni@example.com", "role": "Developer" }
}
```

**Error - missing field (400):**
```json
{ "success": false, "error": "Name is required" }
```

**Error - invalid email format (400):**
```json
{ "success": false, "error": "Invalid email format" }
```

**Error - duplicate email (409):**
```json
{ "success": false, "error": "Email already exists" }
```

### GET /users/\<id\>

Retrieve a single user by ID.

- **Method:** `GET`
- **URL:** `/users/<id>`

**Success (200):**
```json
{
  "success": true,
  "data": { "id": 1, "name": "Saloni", "email": "saloni@example.com", "role": "Developer" }
}
```

**Error - not found (404):**
```json
{ "success": false, "error": "User not found" }
```

## Database Schema

**Database:** `users` · **Table:** `users`

| Column | Type | Constraints |
|---|---|---|
| `id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` |
| `name` | `VARCHAR(120)` | `NOT NULL` |
| `email` | `VARCHAR(255)` | `NOT NULL`, `UNIQUE` |
| `role` | `VARCHAR(50)` | `NOT NULL` |

See [`database/init.sql`](database/init.sql) for the exact DDL.

## Error Handling

- **400 Bad Request** - missing/invalid field, invalid email format, invalid pagination parameters, malformed JSON body.
- **404 Not Found** - user ID doesn't exist, or the route itself doesn't exist.
- **405 Method Not Allowed** - wrong HTTP method for a valid route.
- **409 Conflict** - email already exists.
- **500 Internal Server Error** - unexpected/unhandled errors; logged server-side, never exposes internals to the client.

All of the above are handled centrally in `app/errors.py` so every response - expected or not - comes back as JSON in the same `{"success": false, "error": "..."}` shape.

## Assumptions

- Email is treated as the unique identifier for a user (case-insensitive: `Saloni@Example.com` and `saloni@example.com` are the same email).
- Pagination defaults to `page=1`, `limit=10` when not specified; `limit` is capped at `100` to prevent unbounded queries. `page`/`limit` values below `1`, or non-numeric, return a `400`.
- Search matches a substring against `name` OR `email`, case-insensitively.
- No authentication is required, since it was not part of the mandatory requirements (see the optional JWT section below for what was intentionally left out).
- Only `name`, `email`, and `role` are accepted on create; any other fields in the request body are ignored.

## Testing

Tests run against a **real MySQL database** (never SQLite), using a dedicated test database so the main `users` database is never touched.

1. Make sure `TEST_DATABASE_URL` in `.env` points at a database with `test` in its name (e.g. `users_test`) - the test suite refuses to run otherwise, as a safety net against accidentally wiping a real database.
2. Run:
   ```bash
   pytest tests/ -v
   ```

The suite (`tests/test_users.py`) covers: empty listing, successful creation, missing `name`/`email`/`role`, invalid email format, duplicate email, fetching an existing/non-existing user, search by name/email (including case-insensitivity), pagination (including page boundaries and invalid parameters), unknown routes, wrong HTTP methods, and malformed JSON bodies.

## AI Usage Declaration
## AI tools used:

ChatGPT

GitHub Copilot

AI-generated assistance:

ChatGPT: Initial project structure and Flask application factory setup, boilerplate for the model, schema, service, and route layers, suggestions for API architecture and error-handling design, documentation structure and this README, the optional React/Vite/Tailwind admin UI (component structure, glassmorphism styling, API client)

GitHub Copilot: Bug fixes and error resolution, environment setup troubleshooting, additional code generation and refinement

Manual verification performed:

Every endpoint was manually tested end-to-end against a real, running MySQL instance (via curl), including all success and error paths described above

The full pytest suite was run against a real MySQL test database (not mocked, not SQLite) and confirmed passing

A real bug in the test fixture (an app-context leak causing the test teardown to deadlock against MySQL's metadata lock) was diagnosed and fixed during development, not left in place

Configuration, .gitignore, and .env/.env.example were reviewed to confirm no secrets are committed

Code was reviewed for unused imports/dead code (via pyflakes) and for architectural compliance with the required layering

The admin UI was actually run (Vite dev server + Flask API together) and driven with a headless browser to confirm it renders correctly, calls the real API, and displays real backend validation errors, in both light and dark themes and at a mobile viewport width - not just visually inspected as static code

## Short Answers

### 1. Why did you choose Flask?

Flask is lightweight and unopinionated, which suits a small, well-defined API like this one - there's no ORM-agnostic admin site, template engine, or forms library to configure and then ignore, as you'd get with Django. Routing is explicit and easy to follow, the application factory pattern keeps configuration environment-based and testable, and the whole framework is small enough that every layer of this project (routing, validation, error handling) can be understood by reading a handful of short files.

### 2. How would you scale this system?

- **Horizontally**: run multiple stateless Flask instances (e.g. via Gunicorn workers) behind a load balancer - the app holds no in-memory state, so this works without changes.
- **Database**: add indexes on `email` (already implied by the UNIQUE constraint) and consider one on `name` if search volume grows; use connection pooling (already configured via SQLAlchemy's engine); introduce read replicas for read-heavy traffic (most of this API's traffic is `GET /users`).
- **Caching**: a cache like Redis in front of frequently-read, rarely-changed data (e.g. a specific user by ID) can reduce database load.
- **Background jobs**: if user creation ever triggers side effects (emails, audit logs), move those to a task queue (e.g. Celery/RQ) so the request/response cycle stays fast.
- **Observability**: centralized logging and monitoring (e.g. structured logs shipped to a log aggregator, metrics/alerts) to see problems before users report them.

This is deliberately more than the current assignment needs - the point is the architecture (stateless app, thin routes, no logic tied to a single process) doesn't need to change to get there.

### 3. What changes would you make for production?

- **Authentication/authorization** on write endpoints (and possibly reads), e.g. JWT or API keys.
- **HTTPS** everywhere, terminated at a reverse proxy (e.g. Nginx) in front of the app.
- **Secrets management** (e.g. a vault or the platform's secret store) instead of a `.env` file.
- **Production WSGI server** (e.g. Gunicorn/Waitress) instead of Flask's development server, behind a reverse proxy.
- **Database migrations** (e.g. Alembic) instead of a one-off `init.sql`, so schema changes are versioned and repeatable.
- **Stronger validation/rate limiting** to protect against abuse.
- **Structured logging and monitoring/alerting** for error rates, latency, and DB health.
- **Automated CI/CD** running the test suite before every deploy.
- **Backups** and a tested restore process for the database.
- **Security headers** and an explicit **CORS policy** (currently not needed since there's no frontend consuming this cross-origin).
- **Environment-specific configuration** (separate settings and credentials per environment, already partly in place via `config.py`).

## Explanation

**1. How a request flows through the application**
A request hits a Flask route (e.g. `POST /users`). The route reads the JSON body, hands it to the validation schema, and - if valid - calls a function in the service layer. The service layer talks to the database through the SQLAlchemy model and returns a plain dictionary. The route wraps that dictionary in the standard `{"success": true, "data": ...}` shape and returns it as JSON. If anything goes wrong at any step, an exception is raised and a central error handler turns it into a JSON error response with the right HTTP status code.

**2. Why routes and services are separated**
Routes only deal with HTTP concerns (reading the request, returning a response). Services contain the actual business rules (checking for duplicate emails, building search queries, doing pagination math). This means the business logic can be tested and reasoned about without needing to simulate an HTTP request, and the route functions stay short enough to read in a few seconds.

**3. How SQLAlchemy interacts with MySQL**
The `User` model is a Python class that maps to the `users` table. SQLAlchemy translates method calls like `User.query.filter(...)` or `db.session.add(user)` into SQL statements, sends them to MySQL through the PyMySQL driver, and converts the rows that come back into `User` objects. We never write raw SQL by hand for normal operations.

**4. How validation works**
A Marshmallow schema declares the three required fields (`name`, `email`, `role`). Custom validators check each field is present and non-blank, and that `email` matches a basic email pattern. If validation fails, we pick a single, clear error message (in a fixed field order) and return it with a `400` status - so the client always gets one specific reason, not a wall of errors.

**5. How duplicate email is handled**
Before inserting, the service checks whether a user with that email (case-insensitively) already exists, and returns `409` immediately if so. As a second, database-enforced layer, the `email` column has a `UNIQUE` constraint - so even if two requests with the same new email arrive at almost the same instant, only one insert can succeed; the other fails at the database level and is converted into the same `409` response. This is what actually guarantees correctness under concurrency, not just the upfront check.

**6. How search works**
`GET /users?search=term` filters rows where `name` OR `email` contains `term`, case-insensitively, using a `LIKE` query built with SQLAlchemy - the database does the filtering, not Python.

**7. How pagination works**
`page` and `limit` query parameters are parsed and validated (must be positive integers, `limit` capped at 100). SQLAlchemy's `.paginate()` then issues a `LIMIT`/`OFFSET` query at the database level, so only the requested page of rows is ever loaded into memory - not the whole table.

**8. Why different HTTP status codes are used**
Status codes tell the client what kind of outcome happened without it having to parse the error message: `200`/`201` for success, `400` for a problem with the request itself (validation), `404` for something that doesn't exist, `409` for a conflict with existing data (duplicate email), `405` for using the wrong HTTP method, and `500` for something unexpected on the server. This is standard REST practice and makes the API predictable to integrate with.

**9. How the application could scale**
Because the app is stateless (no data stored in memory between requests), you can run many copies of it behind a load balancer without any code changes. The database is the part that needs the most attention as load grows - indexing, connection pooling, and eventually read replicas or caching.

**10. What would be changed for production**
Add authentication, run behind HTTPS with a real WSGI server, move secrets out of `.env` into a proper secrets manager, use database migrations instead of a static SQL file, and add monitoring/logging so problems are visible before they become outages.

