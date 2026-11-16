# FaaS Billing

MVP системы биллинга для FaaS-сервисов: приём метрик выполнения функций, статистика и расчёт стоимости по тарифам.

**Стек:** FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 16 · nginx + статический фронт (чистый HTML/CSS/JS).

---

## 1. Быстрый запуск (Docker)

Нужен установленный Docker с Compose v2 (`docker compose version`).

```bash
# из корня проекта
docker compose up --build
```

Что произойдёт:

1. поднимется PostgreSQL (`db`) и дождётся готовности (healthcheck);
2. `backend` применит миграции Alembic (`alembic upgrade head`) и запустит uvicorn;
3. `frontend` (nginx) отдаст UI и проксирует `/api/*` на backend.

| Что            | Адрес                                |
|----------------|--------------------------------------|
| Веб-интерфейс  | http://localhost:3000                |
| Swagger / API  | http://localhost:8000/docs           |
| PostgreSQL     | `localhost:5432` (faas / faas / faas_billing) |

### Полезные команды

```bash
docker compose up -d --build        # запуск в фоне
docker compose logs -f backend      # логи backend
docker compose ps                   # состояние сервисов
docker compose down                 # остановить (данные БД сохранятся)
docker compose down -v              # остановить и удалить данные БД
docker compose exec db psql -U faas faas_billing   # консоль PostgreSQL
```

### Настройка

Значения по умолчанию подходят «из коробки». Чтобы поменять, создайте файл `.env` рядом с `docker-compose.yml`
(Compose подхватит его автоматически):

```env
POSTGRES_USER=faas
POSTGRES_PASSWORD=change-me
POSTGRES_DB=faas_billing
```

> Существующий `.env.example` (с `localhost` в `DATABASE_URL`) нужен только для запуска **без Docker**.
> В контейнере `DATABASE_URL` задаётся в `docker-compose.yml` и указывает на хост `db`.

### Сценарий проверки через UI

1. Вкладка **Клиенты** → создайте клиента.
2. **Тарифы** → создайте тариф (значения подставлены по умолчанию).
3. **Функции** → создайте функцию, выбрав клиента и тариф.
4. **Метрики** → отправьте событие или нажмите «Сгенерировать 10 случайных событий».
5. **Биллинг** → выберите функцию (период необязателен) → «Рассчитать».

---

## 2. Запуск без Docker (для разработки backend)

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

cp .env.example .env                 # DATABASE_URL указывает на localhost:5432
docker compose up -d db              # PostgreSQL можно поднять только контейнером
alembic upgrade head
uvicorn app.main:app --reload        # http://localhost:8000/docs

pytest                               # тесты идут на SQLite in-memory, БД не нужна
```

Если запускаете UI отдельно (не через nginx), добавьте в `app/main.py` CORS:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])
```

---

## 3. Структура проекта

```
faas_billing-backend/
├── app/                        # backend-приложение
│   ├── main.py                 # создание FastAPI, подключение роутеров (/api/v1)
│   ├── core/
│   │   ├── config.py           # настройки из переменных окружения / .env
│   │   └── database.py         # engine, SessionLocal, Base, зависимость get_db
│   ├── models/                 # SQLAlchemy-модели (таблицы)
│   │   ├── client.py           # Client
│   │   ├── tariff.py           # Tariff + TariffVersion (версионирование цен)
│   │   ├── function.py         # FaasFunction (клиент + тариф)
│   │   └── metric.py           # Metric (событие выполнения функции)
│   ├── schemas/                # Pydantic-схемы запросов/ответов
│   ├── api/routes/             # HTTP-эндпоинты
│   │   ├── clients.py          # POST/GET /clients
│   │   ├── tariffs.py          # POST/GET /tariffs
│   │   ├── functions.py        # POST/GET /functions
│   │   ├── metrics.py          # POST/GET /metrics, GET /metrics/stats
│   │   └── billing.py          # GET /billing/functions/{id}/cost
│   └── services/               # бизнес-логика
│       ├── pricing.py          # расчёт стоимости (Decimal, минимумы 100 мс / 128 МБ)
│       └── metrics.py          # агрегация статистики
├── migrations/                 # Alembic (0001_initial_tables.py)
├── tests/                      # pytest: расчёт цены и API
├── docs/                       # ER-диаграмма (dbml + png)
├── frontend/                   # базовый UI (можно удалить/заменить)
│   ├── index.html              # разметка: 5 вкладок
│   ├── style.css
│   ├── app.js                  # fetch к /api/v1, отрисовка таблиц и форм
│   ├── nginx.conf              # статика + прокси /api → backend:8000
│   └── Dockerfile
├── Dockerfile                  # образ backend
├── docker-compose.yml          # db + backend + frontend
├── .dockerignore
├── pyproject.toml · alembic.ini · .env.example
└── README.md
```

### Как это работает

**Данные.** `Client` владеет функциями; `FaasFunction` привязана к `Tariff`; у тарифа есть версии
(`TariffVersion`) с четырьмя ценами: за вызов, за мс, за ГБ·с, доплата за cold start. Каждое событие — `Metric`
с уникальным `event_id` (повторная отправка → `409`, это защита от дублей).

**Расчёт стоимости** (`services/pricing.py`) для каждого события:
- длительность округляется вверх до минимума 100 мс, память — до 128 МБ;
- `ГБ·с = память_МБ / 1024 × длительность_мс / 1000`;
- итог = вызовы × цена + мс × цена + ГБ·с × цена + cold_starts × доплата, каждая статья округляется до 6 знаков.

Деньги — всегда `Decimal`, в JSON уходят строками.

**API** (все пути с префиксом `/api/v1`):

| Метод | Путь | Назначение |
|---|---|---|
| POST / GET | `/clients` | создать / список клиентов |
| POST / GET | `/tariffs` | создать / список тарифов |
| POST / GET | `/functions` (`?client_id=`) | создать / список функций |
| POST / GET | `/metrics` (`?function_id=`) | принять событие / список |
| GET | `/metrics/stats` (`function_id, client_id, date_from, date_to`) | агрегаты по функциям |
| GET | `/billing/functions/{id}/cost` (`date_from, date_to`) | стоимость за период |

Пример без UI:

```bash
curl -X POST localhost:8000/api/v1/clients -H 'Content-Type: application/json' -d '{"name":"ACME"}'
curl "localhost:8000/api/v1/billing/functions/1/cost?date_from=2026-11-01T00:00:00Z"
```

**Docker-сеть.** Сервисы видят друг друга по имени: backend → `db:5432`, nginx → `backend:8000`.
Браузер ходит только на `localhost:3000`, поэтому CORS не нужен. Данные БД лежат в volume `pgdata`.

---

## 4. Частые проблемы

| Симптом | Причина / решение |
|---|---|
| `port is already allocated` | порт занят — поменяйте левую часть в `ports:` (например `"3001:80"`) |
| backend перезапускается | смотрите `docker compose logs backend`; чаще всего неверный `DATABASE_URL` / пароль БД |
| Поменяли пароль в `.env`, а БД не принимает | volume хранит старый пароль: `docker compose down -v` и запуск заново |
| UI открывается, но «Не удалось загрузить данные» | backend ещё стартует или упал — проверьте логи |
