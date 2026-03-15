# SentinelAPI (api_fortress)

FastAPI-based security and analytics API with JWT auth, API keys, rate limiting, and anomaly detection.

## Requirements

- Python 3.10+ (you are using 3.13)
- PostgreSQL running locally (default):
  - host: `localhost`
  - port: `5432`
  - user: `postgres`
  - password: `postgres`
  - database: `api_fortress_db`
- `virtualenv` or similar

You can override the DB connection with `DATABASE_URL`:

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DBNAME"
```

## Setup

```bash
cd api_fortress
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt  # if present
```

If you don't have a `requirements.txt` yet, install the core deps:

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic passlib python-jose[cryptography] pydantic
```

## Database & Alembic

Alembic is configured under `alembic/` with `alembic.ini` at the project root.
It uses the same `DATABASE_URL` as the app and auto-loads models from `app.database.Base`.

### Initialize / create migrations

Create a new migration after changing models:

```bash
alembic revision -m "describe change"
```

Apply all migrations:

```bash
alembic upgrade head
```

Downgrade one step:

```bash
alembic downgrade -1
```

> Note: For now, the app also calls `Base.metadata.create_all(bind=engine)` on startup
> to make initial development easy. In a production setup you would typically rely
> on Alembic migrations only and remove that auto-create call.

## Running the API

```bash
uvicorn app.main:app --reload --port 8001
```

- Swagger UI: `http://127.0.0.1:8001/docs`
- OpenAPI JSON: `http://127.0.0.1:8001/openapi.json`

## Basic usage flow

1. **Register** via `POST /auth/register`.
2. **Login** via `POST /auth/login` and copy the `access_token`.
3. **Create API key** via `POST /api-keys/` using the JWT.
4. For protected routes, send:
   - `Authorization: Bearer <access_token>`
   - `X-API-Key: <api_key>`

