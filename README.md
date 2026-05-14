# Event Management API

Django REST Framework API for managing events (conferences, meetups, etc.) and user registrations, with JWT authentication, OpenAPI documentation, Docker support, search and filtering, and email notifications when users register.

## Features

- **Events**: `title`, `description`, `date`, `location`, `organizer` (linked to the authenticated user who created the event). Full CRUD; only the organizer may update or delete an event. Anyone may list and retrieve events (read-only without auth).
- **Authentication**: Register (`POST /api/auth/register/`) and obtain JWT tokens (`POST /api/auth/token/`, refresh at `/api/auth/token/refresh/`).
- **Event registration**: Authenticated users register with `POST /api/events/{id}/register/`, cancel with `DELETE /api/events/{id}/register/`, list their registrations at `GET /api/my-registrations/`, or delete by registration id at `DELETE /api/registrations/{id}/`.
- **Search and filtering (bonus)**: `?search=`, `?location=`, `?organizer=`, `?date_from=`, `?date_to=`, plus ordering e.g. `?ordering=date` or `?ordering=-title`.
- **Email notifications (bonus)**: On successful registration, an email is sent if the user has an `email` address. Default backend in development is the console (messages appear in the server log).
- **API docs**: OpenAPI schema at `/api/schema/`, Swagger UI at `/api/docs/`.

## Quick start (local, SQLite)

Python **3.12–3.x** (`requires-python` in `pyproject.toml`: `>=3.12,<4`). Dependencies are declared in `pyproject.toml`; use [uv](https://docs.astral.sh/uv/) or `pip install .` in a virtualenv.

**With uv:**

```bash
uv sync
copy .env.example .env   # Windows — or: cp .env.example .env
set USE_SQLITE=true      # Windows CMD — or in PowerShell: $env:USE_SQLITE="true"
uv run python manage.py migrate
uv run python manage.py createsuperuser   # optional, for /admin/
uv run python manage.py runserver
```

**With venv + pip:**

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS / Linux

pip install .
set USE_SQLITE=true       # Windows CMD
# export USE_SQLITE=true    # macOS / Linux

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Open [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/) for interactive documentation.

## Quick start (Docker + PostgreSQL)

From the project root:

```bash
docker compose up --build
```

Migrations run automatically before Gunicorn starts. API: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/).

## Environment variables

Copy `.env.example` to `.env` and adjust. Important variables:

| Variable | Purpose |
|----------|---------|
| `USE_SQLITE` | Set to `true` for local SQLite; omit or `false` for Postgres settings below. |
| `POSTGRES_*` | Database connection when not using SQLite. |
| `DJANGO_SECRET_KEY` | Secret key; required when `DJANGO_DEBUG` is not `true`. |
| `DJANGO_DEBUG` | `true`/`false`. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames. |
| `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL` | Email delivery; see [Django email settings](https://docs.djangoproject.com/en/stable/topics/email/). |

## API overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register/` | No | Create user (`username`, `email`, `password`). |
| POST | `/api/auth/token/` | No | JWT pair (`username`, `password`). |
| POST | `/api/auth/token/refresh/` | No | Refresh token body: `{"refresh": "..."}`. |
| GET | `/api/events/` | No | List events (filters/search below). |
| POST | `/api/events/` | Yes | Create event (you become organizer). |
| GET | `/api/events/{id}/` | No | Event detail. |
| PUT/PATCH | `/api/events/{id}/` | Yes | Organizer only. |
| DELETE | `/api/events/{id}/` | Yes | Organizer only. |
| POST | `/api/events/{id}/register/` | Yes | Register for event. |
| DELETE | `/api/events/{id}/register/` | Yes | Cancel registration for that event. |
| GET | `/api/my-registrations/` | Yes | List current user’s registrations. |
| GET | `/api/my-registrations/{id}/` | Yes | Registration detail. |
| DELETE | `/api/registrations/{id}/` | Yes | Cancel by registration id (owner only). |
| GET | `/api/schema/` | No | OpenAPI 3 schema (YAML by default; JSON with `Accept: application/vnd.oai.openapi+json` or your client’s equivalent). |
| GET | `/api/docs/` | No | Swagger UI. |

**Query parameters on `GET /api/events/`**

- `search` — matches `title`, `description`, `location`.
- `ordering` — allowed fields: `date`, `title` (prefix `-` for descending, e.g. `-date`).
- `location` — case-insensitive partial match.
- `organizer` — user id of organizer.
- `date_from`, `date_to` — ISO 8601 datetimes (inclusive range on `date`).

## Example requests

### 1. Register

|   | Fill in |
|------------|---------|
| Method | `POST` |
| URL | `http://127.0.0.1:8000/api/auth/register/` |
| **Body** tab | **raw** → dropdown **JSON** |
| Body text | See JSON below |

```json
{
  "username": "person",
  "email": "person@example.com",
  "password": "password"
}
```

**Send** → expect **201 Created**.

### 2. Get JWT (login)

|   | Fill in |
|------------|---------|
| Method | `POST` |
| URL | `http://127.0.0.1:8000/api/auth/token/` |
| **Body** → **raw** → **JSON** | See JSON below |

```json
{
  "username": "person",
  "password": "password"
}
```

**Send** → copy the **`access`** string from the response (you will paste it in the next request).

### 3. Create event (needs auth)

|   | Fill in |
|------------|---------|
| Method | `POST` |
| URL | `http://127.0.0.1:8000/api/events/` |
| **Authorization** tab | Type **Bearer Token** |
| **Token** field | Paste **only** the `access` value (Postman adds the `Bearer` word) |
| **Body** → **raw** → **JSON** | See JSON below |

```json
{
  "title": "Django Meetup",
  "description": "Talks and pizza",
  "date": "2026-06-01T18:00:00Z",
  "location": "Berlin"
}
```

**Send** → expect **201 Created**.

### 4. List events (optional query params)

|   | Fill in |
|------------|---------|
| Method | `GET` |
| URL | `http://127.0.0.1:8000/api/events/` |
| **Params** tab (Query Params) | Add rows **Key** / **Value** (see examples below) |

Example rows — add only what you need; leave others empty:

| Key | Example value | Effect |
|-----|-----------------|--------|
| `search` | `Django` | Search in title, description, location |
| `location` | `Berlin` | Location contains (case-insensitive) |
| `organizer` | `1` | Filter by organizer user id |
| `date_from` | `2026-06-01T00:00:00Z` | Event `date` ≥ this |
| `date_to` | `2026-12-31T23:59:59Z` | Event `date` ≤ this |
| `ordering` | `-date` | Sort: `-date` or `date`, `-title` or `title` |

**Send** → expect **200 OK** and a JSON list.

### 5. Refresh JWT (optional)

|   | Fill in |
|------------|---------|
| Method | `POST` |
| URL | `http://127.0.0.1:8000/api/auth/token/refresh/` |
| **Body** → **raw** → **JSON** | `{"refresh": "<paste refresh from login response>"}` |

## Project layout

- `config/` — Django settings and root URLs.
- `accounts/` — Registration and JWT endpoints.
- `events/` — Models, serializers, views, filters, registration email signal.

