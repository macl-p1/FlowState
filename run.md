# OrchestrAI — Run Instructions

## Prerequisites

| Tool        | Version       | Notes                          |
|-------------|---------------|--------------------------------|
| Python      | >= 3.11       | 3.13 recommended               |
| Node.js     | >= 18         | 20 LTS recommended             |
| npm         | >= 9          | Comes with Node.js             |
| PostgreSQL  | >= 15         | Optional — SQLite used by default |

## Quick Start (SQLite — no database required)

### 1. Clone and enter the project

```bash
git clone <repo-url> OrchestrAI
cd OrchestrAI
```

### 2. Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy env file (first time only)
cp .env.example .env

# Start the API server (SQLite by default)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API starts at **http://localhost:8000**.
- Health check: `GET http://localhost:8000/api/health`
- Swagger docs: `http://localhost:8000/docs`

### 3. Frontend

In a new terminal:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

The UI starts at **http://localhost:3000**.

## Running with Docker (PostgreSQL)

```bash
# Make sure Docker is running, then:
docker compose up --build
```

- Backend: **http://localhost:8000**
- Frontend: **http://localhost:3000**
- Database: PostgreSQL on `localhost:5432`

Set `ANTHROPIC_API_KEY` in `.env` (or pass it via `docker compose` env) for AI features.

## Project Structure

```
OrchestrAI/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers (workflows, runs, approvals, tools)
│   │   ├── database/         # SQLAlchemy models, sessions, base
│   │   ├── engine/           # LangGraph workflow runner & compiler
│   │   ├── agents/           # Agent definitions & tool registry
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── main.py           # FastAPI entry point
│   │   └── config.py         # Settings (env vars)
│   ├── tests/                # Pytest test suite (94 tests)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Shared React components
│   │   └── lib/              # Utils, types
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Running Tests

### Backend

```bash
cd backend
pytest tests/ -v          # verbose
pytest tests/ -q           # quiet summary
```

All 94 tests use an in-memory SQLite database with transaction-based isolation — no PostgreSQL needed.

### Frontend

```bash
cd frontend
npx next build            # type-check + production build
```

## API Endpoints

| Prefix           | Purpose                          |
|------------------|----------------------------------|
| `GET  /api/health` | Health check                    |
| `/api/workflows`  | CRUD for workflow definitions    |
| `/api/runs`       | Start workflows, get run status  |
| `/api/approvals`  | List/approve/reject pending approvals |
| `/api/tools`      | Registered tool actions          |

## Common Issues

- **Backend won't start**: Ensure `.env` exists in `backend/` (copy from `.env.example`).
- **Frontend build fails**: Run `npm install` to refresh dependencies.
- **CORS errors**: Check `CORS_ORIGINS` in `.env` matches your frontend URL.
- **AI features don't work**: Set `ANTHROPIC_API_KEY` in `.env`.

## Default Data

When the backend starts, it auto-seeds:
- 12 demo workflows
- Pre-registered tools (search_database, send_email, validate_invoice, etc.)
