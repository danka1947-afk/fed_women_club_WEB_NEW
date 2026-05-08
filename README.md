# Federal Women Club WEB

MVP web/backend skeleton based on club subscription platform.

Проект пока находится на этапе переноса skeleton из существующей клубной web/backend платформы. В этом PR не проводится глубокий ребрендинг, не меняется бизнес-логика и не удаляются старые MVP flows.

## Структура

- `app/` — backend application skeleton.
- `alembic/` — migration environment and migration versions.
- `scripts/` — operational helper scripts.
- `tests/` — backend tests.
- `frontend/` — frontend MVP skeleton.
- `docs/` — project documentation.

## Локальный запуск backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment

Use `.env.example` as a safe local template. Do not commit real `.env` files or production secrets.

Key placeholders:

```bash
WEB_PUBLIC_URL=https://women-club.example
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Alembic

```bash
alembic heads
alembic upgrade head
```

## Frontend

```bash
cd frontend
npm install
npm run build
```

## Checks

```bash
python -m compileall app scripts
pytest -q
alembic heads
cd frontend && npm run build
```
