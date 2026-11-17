# Chat2Chat

A social feed application with a **Flask + PostgreSQL REST API** (JWT auth, validation, migrations, 94 automated tests) and a React client that can run entirely on mock data for a zero-cost live demo.

**Live demo:** _add your link here_ &nbsp;|&nbsp; **Screenshot / GIF:** _add `docs/screenshot.png` here_

> The live demo runs the frontend in **Demo Mode** on in-browser sample data (nothing is sent to a server and changes are not saved). The real Flask backend is run locally, see [Local setup](#local-setup).

## Features

- Account registration and login with JWT bearer tokens and server-side roles
- Posts with optional image upload; edit and delete restricted to the author
- Comments, follow/unfollow, profile and cover photos
- Simulated free/premium plan switch (no real payment is taken)
- Input validation with field-level errors, uniform JSON error format, correct HTTP status codes
- Rate-limited auth endpoints, enumeration-safe login, hashed passwords (scrypt)
- Safe uploads: extension allow-list + magic-byte check, random filenames, size limit
- Alembic migrations, health-check endpoint, Procfile for deployment
- Frontend **Demo Mode**: full app with create/edit/delete working in memory, "Try Demo" login

## Tech stack

**Backend:** Python 3.12, Flask 3, Flask-SQLAlchemy / SQLAlchemy 2, Flask-Migrate (Alembic), Flask-JWT-Extended, marshmallow, Flask-Limiter, Flask-CORS, PostgreSQL (SQLite for zero-setup dev and tests), gunicorn, pytest + pytest-cov

**Frontend:** React 18, React Router 6, Material UI icons, Bootstrap, axios (Create React App)

## Architecture

```mermaid
flowchart LR
    subgraph Browser
        UI[React components] --> API["api/index.js"]
        API -- "REACT_APP_DEMO_MODE=false" --> REAL[realApi.js<br/>axios + JWT]
        API -- "REACT_APP_DEMO_MODE=true" --> MOCK[mockApi.js<br/>in-memory state]
    end
    REAL -- "HTTPS /api/v1" --> FLASK
    subgraph Backend
        FLASK[Flask app factory] --> BP[Blueprints<br/>auth · users · posts · comments · follows]
        BP --> SCH[marshmallow schemas]
        BP --> ORM[SQLAlchemy models]
        ORM --> DB[(PostgreSQL)]
        BP --> FS[(uploads/)]
    end
```

```
backend/
  app/
    __init__.py      # create_app() factory
    config.py        # Development / Testing / Production, all from env vars
    models.py        # User, Post, Comment, Follow
    schemas.py       # request validation
    errors.py        # ApiError + uniform JSON error handlers
    uploads.py       # safe image storage
    api/             # one blueprint per resource
  migrations/        # Alembic
  tests/             # pytest suite
  wsgi.py            # gunicorn / flask entry point
frontend/src/
  api/               # realApi.js, mockApi.js, mockData.js, index.js (switch)
  context/           # AuthContext
  components/, pages/
```

## API endpoints

Base path: `/api/v1`. Successful responses are `{"status": <code>, "data": ...}`; errors are `{"status": <code>, "message": "...", "errors": {...}}`.

| Method | Route | Description | Auth |
|---|---|---|---|
| GET | `/health` | Liveness and database check | No |
| POST | `/register` | Create an account (role is always `user`) | No |
| POST | `/login` | Log in with username or email, returns JWT | No |
| GET | `/user` | List users (public fields only) | No |
| GET | `/user/<id>` | Get one user | No |
| GET | `/user/me` | Current user, including email | Yes |
| PUT | `/user/profile` | Set `personPic` / `coverPic` | Yes |
| PUT | `/premium` | Simulated plan change (`user` or `premium`) | Yes |
| POST | `/upload-photo` | Upload an image (multipart field `photo`) | Yes |
| GET | `/post` | Feed, newest first (`?limit=&offset=`, max 100) | No |
| POST | `/post` | Create a post (JSON or multipart with `photo`) | Yes |
| GET | `/post/<id>` | Get a post with its comments | No |
| PUT | `/post/<id>` | Edit own post | Yes |
| DELETE | `/post/<id>` | Delete own post | Yes |
| GET | `/mypost` | Posts of the current user | Yes |
| POST | `/comment/<post_id>` | Comment on a post | Yes |
| GET | `/comments/<post_id>` | List comments of a post | No |
| GET | `/comment/<id>` | Get one comment | No |
| POST | `/follow/<user_id>` | Follow a user | Yes |
| POST | `/unfollow/<user_id>` | Unfollow a user | Yes |
| GET | `/following` | Users the current user follows | Yes |

Authenticated routes expect `Authorization: Bearer <token>`. Login is limited to 5 requests/minute and registration to 10/minute per IP.

## Local setup

Prerequisites: Python 3.12+, Node 18+. PostgreSQL is optional (SQLite is used if `DATABASE_URL` is unset).

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                # then edit values (never commit .env)

flask --app wsgi db upgrade         # create the tables
flask --app wsgi run                # http://127.0.0.1:5000
```

**Environment variables** (see `.env.example`):

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development` (default) or `production` |
| `SECRET_KEY`, `JWT_SECRET_KEY` | Required in production; random per-process values are generated in development |
| `DATABASE_URL` | e.g. `postgresql://chat2chat:chat2chat@localhost:5432/chat2chat`. Defaults to a local SQLite file |
| `CORS_ORIGINS` | Comma-separated allowed browser origins (default `http://localhost:3000`) |
| `JWT_ACCESS_MINUTES` | Token lifetime, default 60 |

**PostgreSQL via Docker:** `docker compose up -d db` from the repo root, then set `DATABASE_URL` as above and run `flask --app wsgi db upgrade`.

**Production:** set `APP_ENV=production` plus the three required variables (the app refuses to start without them) and run `gunicorn wsgi:app` (see `Procfile`).

### Run the tests

```bash
cd backend
pytest              # 94 tests, coverage report included
```

Tests use an in-memory SQLite database, so no external services are needed.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm start                # real backend, http://localhost:3000
npm run start:demo       # demo mode, no backend needed
npm run build:demo       # production build in demo mode
```

## Live demo note

The deployed demo is the frontend only, built with `REACT_APP_DEMO_MODE=true`. In that mode `src/api/mockApi.js` replaces the HTTP client, so all data is fictional sample data held in memory and resets on reload. Use the **Try Demo** button on the login page. The Flask backend is not hosted; run it locally with the steps above to use the real API.

## Deploying the demo (Vercel)

1. Push the repo to GitHub.
2. In Vercel choose **Add New → Project**, import the repo and set **Root Directory** to `frontend`.
3. Deploy. `vercel.json` sets the build output, demo mode and the SPA rewrite so deep links such as `/comments?id=1` work.

## Author

**Daniel Mungai**
GitHub: [github.com/mungaiDaniel](https://github.com/mungaiDaniel) · LinkedIn: [linkedin.com/in/daniel-mungai-7a52451b8](https://linkedin.com/in/daniel-mungai-7a52451b8)
