# Django Backend Boilerplate

A minimal, batteries-included Django + Django REST Framework backend template.
It ships with **JWT authentication and user/organization management already built in**,
so you can drop in new "apps" (feature modules) and start building APIs immediately.

## What's included

- **Auth** (`apps/authentications`): signup, login (JWT), token refresh/verify, password reset & change.
- **Users** (`apps/users`): custom `User` model (email login) + `Organization` model and admin
  user/organization management APIs.
- **REST framework** with JWT auth, pagination, a standard response envelope (`utils/response`),
  and a custom exception handler.
- **Swagger/OpenAPI** docs at `/docs/` (via `drf-yasg`).
- **Celery** wiring (`core/celery.py`) for background jobs (optional; needs Redis).
- **App scaffold** (`conf/app_template`) to generate new feature apps in a consistent layout.
- Shared helpers under `utils/` (pagination, serializers, choices, base models, permissions, etc.).

## Prerequisites

- **Python 3.11+**
- (Optional) **Redis** — only needed if you run Celery workers/beat.

## Getting started

### 1. Create a virtual environment & install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

The defaults use local **SQLite** and dummy keys, which is enough for development.
Edit `.env` to point at PostgreSQL or set real integration keys as needed.

### 3. Migrate the database

```bash
python manage.py migrate
```

### 4. (Optional) Create an admin user

```bash
python manage.py shell -c "from apps.users.models import User; u=User.objects.create_user(email='admin@example.com', name='admin', password='AdminPass123'); u.is_staff=u.is_superuser=True; u.save()"
```

### 5. Run the development server

```bash
python manage.py runserver
```

## Running Celery (background jobs)

This project uses Celery for background tasks like receipt processing.

### 1. Make sure Redis is running

```bash
redis-server
```

If you dont have redis installed:
```bash
# mac
brew install redis

# ubuntu/debian
sudo apt install redis-server
```

### 2. Set Celery env vars in `.env`

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Start the celery worker

Open a new terminal, activate your venv, then run:

```bash
cd backend
source /venv/bin/activate.ps1
celery -A core worker -l info
```

This picks up and runs background tasks like receipt analysis jobs.

### 4. (Optional) Start celery beat

Only needed if you have scheduled/periodic tasks:

```bash
celery -A core beat -l info
```

Keep this running alongside your django server and worker while developing features that use background jobs.

### Gemini API Key

This project uses Google Gemini API for receipt analysis.

1. Get an API key from https://aistudio.google.com/apikey
2. Add it to your `.env` file:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```


The API is available at http://127.0.0.1:8000/.

## Key endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthcheck/` | Liveness probe (`{"status": "OK"}`) |
| POST | `/auth/signup/` | Register a user, returns JWT tokens |
| POST | `/auth/token/` | Log in, returns JWT tokens |
| POST | `/auth/token/refresh/` | Refresh access token |
| POST | `/auth/change-password/` | Change password (authenticated) |
| GET/POST | `/api/admin/users/` | List/create users (staff only) |
| GET/POST | `/api/admin/organizations/` | List/create organizations (staff only) |
| GET | `/docs/` | Swagger UI (requires admin session via `/admin/`) |
| — | `/admin/` | Django admin |

## Adding a new app (feature module)

A `startapp` template lives in `conf/app_template` and produces the standard
`api/{urls,views,serializers}` layout used by this project.

```bash
mkdir apps/my_feature
python manage.py startapp my_feature apps/my_feature --template conf/app_template --extension py
```

Then:

1. Add `"apps.my_feature"` to `LOCAL_APPS` in `core/settings.py`.
2. Add a route in `core/urls.py`, e.g. `path("my-feature/", include("apps.my_feature.api.urls"))`
   inside `api_urlpatterns`.
3. Define models, serializers, and views; run `makemigrations` / `migrate`.
4. Add tests under `apps/my_feature/tests/` (see conventions in `agents.md`).

## Testing, linting, formatting

```bash
python -m pytest          # run tests (uses unit_test_settings + SQLite)
ruff check .              # lint
black .                   # format
```

## Project layout

```
apps/
  authentications/   # JWT auth endpoints
  users/             # User + Organization models & admin APIs
conf/app_template/   # scaffold for new apps
core/                # settings, urls, wsgi/asgi, celery
utils/               # shared helpers (response, pagination, db, etc.)
```
