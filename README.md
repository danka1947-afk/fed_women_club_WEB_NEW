# Federal Women Club WEB

MVP web/backend skeleton based on club subscription platform.

Проект пока находится на этапе переноса skeleton из существующей клубной web/backend платформы. В этом PR не проводится глубокий ребрендинг, не меняется бизнес-логика и не удаляются старые MVP flows.

Federal Women Club проектируется как федеральный multi-city продукт с первого MVP:

- пользователь выбирает город в VK-боте и/или web;
- партнёр принадлежит одному городу;
- каталог партнёров фильтруется по городу;
- админка и аналитика должны быть готовы к фильтрам по городу;
- подписка в MVP глобальная для клуба, а не отдельная для каждого города;
- филиалы/locations партнёров не вводятся в MVP.

## Категории женского клуба

Централизованный backend-список категорий хранится в `app/core/categories.py`:

- Красота
- Маникюр / педикюр
- Волосы / окрашивание
- Брови / ресницы
- Косметология
- Массаж / SPA
- Фитнес / йога
- Здоровье
- Психология
- Одежда / аксессуары
- Кафе / рестораны
- Обучение / мастер-классы
- Фотосессии
- Цветы / подарки
- Другое

## Структура

- `app/` — backend application skeleton.
- `alembic/` — migration environment and migration versions.
- `scripts/` — operational helper scripts.
- `tests/` — backend tests.
- `frontend/` — frontend MVP skeleton.
- `docs/` — project documentation.

## Multi-city MVP notes

- `City` — минимальный справочник городов (`id`, `name`, `slug`, `is_active`, `sort_order`, `created_at`).
- `Partner.city_id` — nullable связь партнёра с городом для безопасной миграции skeleton-проекта.
- `ClientProfile.selected_city_id` — nullable выбранный город клиента; подписка остаётся глобальной.
- API/catalog план описан в `docs/mvp-spec.md` и подготовлен service-level helper для будущего endpoint.

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
