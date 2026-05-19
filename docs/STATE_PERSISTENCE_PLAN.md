# План переноса `USER_STATE` из in-memory в persistent storage (VK Bot)

## 1) Текущие state keys (инвентаризация)

Ниже — целевой список ключей `USER_STATE`, упомянутых в аудите и обязательных к покрытию при миграции:

- `web_client_token`
- `web_client_session`
- `profile_survey_step`
- `profile_survey_data`
- `last_payment_request`
- `city`
- `catalog_cache`
- `privilege_filter`

> Примечание: если в runtime есть дополнительные ephemeral ключи (например, временные флаги UI/диалога), их нужно добавить в этот же реестр перед стартом работ.

---

## 2) Какие state критичны

Критичные (потеря при рестарте недопустима или сильно ломает UX/бизнес-поток):

1. **`web_client_token` / `web_client_session`**  
   Нужны для связки VK-потока с web-кабинетом, восстановления авторизации и продолжения сценариев.
2. **`profile_survey_step` / `profile_survey_data`**  
   Потеря ломает анкету, заставляет пользователя проходить повторно.
3. **`last_payment_request`**  
   Нужен для корректного отслеживания статуса оплаты и повторных действий пользователя.
4. **`city`**  
   Влияет на релевантность выдачи и контекст сценариев.
5. **`catalog_cache`**  
   Критичен для производительности и стабильности ответа бота.
6. **`privilege_filter`**  
   Важен для персонализированной выдачи и консистентного поведения каталога.

---

## 3) Что можно хранить кратковременно

Кратковременное хранение (TTL, допускается потеря без нарушения финансовых/идентификационных гарантий):

- `catalog_cache` (кэш каталога)
- `privilege_filter` (фильтры, можно восстановить из default/профиля)
- технические курсоры/offset для пагинации
- одноразовые флаги состояния диалога (не связанные с оплатой/идентификацией)

---

## 4) Что нужно хранить надёжно

Надёжное хранение (без потери при рестарте, multi-process-safe):

- `web_client_token`, `web_client_session`
- `profile_survey_step`, `profile_survey_data`
- `last_payment_request`
- `city` (как пользовательская настройка контекста)

Требования:

- устойчивость к рестартам процесса;
- консистентность при нескольких воркерах;
- атомарные обновления (особенно для `last_payment_request` и шагов анкеты);
- наблюдаемость: логирование изменений/ошибок записи.

---

## 5) Вариант Redis

### 5.1 Ключи

Рекомендуемый namespace:

- `vkbot:user:{vk_user_id}:state` — агрегированное состояние пользователя (JSON)
- `vkbot:user:{vk_user_id}:survey` — состояние анкеты (JSON)
- `vkbot:user:{vk_user_id}:session` — web-сессия/токен (JSON)
- `vkbot:user:{vk_user_id}:payment:last` — последний payment request (JSON)
- `vkbot:catalog:{city}:{filter_hash}` — кэш каталога

### 5.2 TTL

Базовые TTL:

- `session` / `web_client_token`: 1–24 часа (по политике безопасности)
- `survey`: 7–30 дней (чтобы пользователь мог вернуться)
- `payment:last`: 30–90 дней (аудит/повторная проверка статуса)
- `city`: без TTL или 180 дней
- `catalog_cache`: 5–30 минут
- `privilege_filter`: 1–7 дней

### 5.3 JSON-структура

Пример агрегированного `state`:

```json
{
  "version": 1,
  "vk_user_id": "123456789",
  "city": "moskva",
  "privilege_filter": {
    "category": "beauty",
    "price_tier": "medium",
    "updated_at": "2026-05-19T10:00:00Z"
  },
  "profile_survey": {
    "step": "contacts",
    "data": {
      "name": "...",
      "phone": "..."
    },
    "updated_at": "2026-05-19T10:00:00Z"
  },
  "session": {
    "web_client_token": "...",
    "web_client_session": "...",
    "expires_at": "2026-05-19T12:00:00Z"
  },
  "last_payment_request": {
    "id": "pr_123",
    "status": "pending",
    "updated_at": "2026-05-19T10:00:00Z"
  },
  "updated_at": "2026-05-19T10:00:00Z"
}
```

### 5.4 Плюсы/минусы

**Плюсы:**

- очень быстрый доступ;
- нативный TTL;
- простая горизонтальная масштабируемость;
- хорошо подходит как state-store + cache.

**Минусы:**

- риск потери части данных при неверной настройке persistence;
- слабее audit trail без дополнительного event log;
- сложнее аналитические выборки по состояниям.

---

## 6) Вариант PostgreSQL

### 6.1 Таблица `bot_user_state`

Рекомендуемая схема:

```sql
CREATE TABLE bot_user_state (
  id BIGSERIAL PRIMARY KEY,
  vk_user_id TEXT NOT NULL UNIQUE,
  state_json JSONB NOT NULL,
  state_version INTEGER NOT NULL DEFAULT 1,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_bot_user_state_updated_at ON bot_user_state(updated_at);
CREATE INDEX ix_bot_user_state_json_gin ON bot_user_state USING GIN (state_json);
```

Опционально (для явной типизации критичных полей):

- `city TEXT`
- `survey_step TEXT`
- `payment_request_id TEXT`
- `session_expires_at TIMESTAMPTZ`

### 6.2 Плюсы/минусы

**Плюсы:**

- высокая надёжность и транзакционность;
- удобный audit/history (через отдельную таблицу событий);
- SQL-аналитика и операционная прозрачность.

**Минусы:**

- выше latency относительно Redis для горячего state;
- TTL не нативный (нужны фоновые джобы очистки);
- дороже для краткоживущего кэша каталога.

---

## 7) Рекомендованный вариант для проекта

**Рекомендация: гибрид Redis + PostgreSQL**

- **Redis**: оперативный пользовательский state и кэш (`catalog_cache`, фильтры, диалоговые шаги).
- **PostgreSQL**: критичные и/или финансово значимые поля (`last_payment_request`, ключевые этапы анкеты, связь с web-session metadata при необходимости аудита).

Если выбирать **один** storage на первом этапе, для минимального time-to-value лучше начать с **Redis** (быстрее внедрение, TTL, минимальные изменения интеграции), а затем закрепить audit-контур в PostgreSQL.

---

## 8) План внедрения по шагам

1. **Инвентаризация и контракт состояния**
   - зафиксировать все ключи `USER_STATE`;
   - описать JSON contract + версионирование (`state_version`).

2. **Абстракция StateRepository**
   - выделить интерфейс `get/set/update/delete`;
   - текущую in-memory реализацию оставить как fallback для dev/tests.

3. **Реализация Redis backend**
   - namespace ключей;
   - TTL-политики;
   - атомарные операции (pipeline/Lua/CAS-подход, где нужно).

4. **(Опционально) PostgreSQL backend для критичных полей**
   - таблица `bot_user_state` или event table;
   - upsert-операции.

5. **Dual-write этап (без остановки текущего flow)**
   - читать из memory (или memory+redis fallback),
   - писать одновременно в memory + persistent backend;
   - сравнивать значения в логах/метриках.

6. **Read-switch**
   - фича-флагом переключить чтение на Redis/PostgreSQL;
   - memory оставить как аварийный fallback на ограниченное время.

7. **Cleanup**
   - отключить memory как source of truth;
   - удалить legacy-пути после стабилизации.

8. **Observability**
   - метрики: hit/miss, latency, deserialization errors, stale state;
   - алерты на рост ошибок записи/чтения.

---

## 9) Какие тесты нужны

1. **Unit-тесты репозитория**
   - set/get/update/delete по всем критичным ключам;
   - TTL-поведение;
   - сериализация/десериализация JSON.

2. **Интеграционные тесты (Redis/PostgreSQL)**
   - конкурентные обновления одного `vk_user_id`;
   - идемпотентность повторных операций;
   - корректность fallback-логики.

3. **Сценарные e2e тесты VK flow**
   - анкета продолжается после рестарта;
   - `last_payment_request` не теряется;
   - city/filter/cached catalog восстанавливаются ожидаемо.

4. **Нагрузочные тесты**
   - p95/p99 latency по чтению state;
   - поведение при пиковых RPS.

5. **Failover-тесты**
   - временная недоступность Redis/PostgreSQL;
   - деградация без потери критичного пользовательского пути.

---

## 10) Миграция без остановки current flow

Подход **expand → migrate → switch → contract**:

1. **Expand**: добавить новый storage и dual-write, не меняя пользовательскую логику.
2. **Migrate**: постепенно прогреть persistent state по активным пользователям.
3. **Switch**: включить read-from-persistent через feature flag (по сегментам пользователей).
4. **Contract**: после периода стабильности отключить чтение из memory.

Практические меры:

- rollout по процентам трафика (5% → 25% → 50% → 100%);
- backout-переключатель (быстрый возврат read-path на старый механизм);
- журнал расхождений state между old/new источниками;
- freeze на удаление legacy до подтверждённой стабильности.

---

## Критерии готовности (Definition of Done)

- после рестарта бота анкета и критичный state пользователя сохраняются;
- `last_payment_request` не теряется;
- работа корректна в multi-process режиме;
- latency и error rate в целевых SLO;
- memory-state больше не является source of truth.
