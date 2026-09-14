# Maison Guillard

Web app for presenting and selling handmade furniture. See
`docs/superpowers/specs/2026-09-14-maison-guillard-mvp-design.md` for the design and
`docs/superpowers/plans/` for implementation plans.

## Local dev setup

1. `docker compose up -d` — starts Postgres on `localhost:5432`.
2. Backend:
   ```
   cd backend
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   cp .env.example .env   # then edit JWT_SECRET, SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD
   .\.venv\Scripts\python.exe -m alembic upgrade head
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 3000
   ```
3. Frontend: (not started yet — S4 in progress)

## Tests

`cd backend && .\.venv\Scripts\python.exe -m pytest -v`
