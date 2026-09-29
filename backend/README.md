# OrchestrAI Backend

Python backend for the Universal Workflow Agent platform.

## Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Environment

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` if you want real LLM planning.

## Tests

```bash
pytest tests/ -v
```
