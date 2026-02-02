# Quiply Backend API

Flask + PostgreSQL. JWT auth.

## Запуск

```bash
pip install -r requirements.txt
python init_db.py
python run.py  # :5001
```

---

## API Reference

Base URL: `/api/v1`

Все ответы в JSON. Ошибки: `{"error": "message"}`.

Авторизация: `Authorization: Bearer <token>`

---

### Health

#### `GET /`

Информация об API.

**Response 200:**
```json
{
  "name": "Quiply API",
  "version": "1.0.0",
  "status": "running",
  "timestamp": "2026-02-01T18:00:00.000000",
  "endpoints": { ... }
}
```

#### `GET /health`

Проверка состояния БД.

**Response 200:**
```json
{
  "status": "ok",
  "database": "healthy",
  "timestamp": "2026-02-01T18:00:00.000000"
}
```

---

### Auth

#### `POST /auth/register`

Регистрация нового пользователя.

**Request:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Response 201:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Response 400:**
```json
{"error": "Username already exists"}
```

---

#### `POST /auth/login`

Получение JWT токена.

**Request:**
```json
{
  "username": "johndoe",
  "password": "secret123"
}
```

**Response 200:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 401:**
```json
{"error": "Invalid credentials"}
```

---

#### `GET /auth/me` 🔒

Текущий пользователь.

**Response 200:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "bio": "Документирую цитаты деда",
  "created_at": "2026-02-01T12:00:00.000000"
}
```

---

### Quips

#### `GET /quips`

Лента quips.

**Query params:**
- `sort` — `smart` (default) или `new`
- `page` — номер страницы (default: 1)

**Response 200:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "username": "johndoe",
    "content": "Интересно девки пляшут",
    "definition": "Реакция на какое-либо событие: восторг, недоумение, ужас, несогласие или радость",
    "usage_examples": "Кот орёт, чтобы его выпустили, выходит… и тут же орёт, чтобы впустили обратно",
    "created_at": "2026-02-01T15:30:00.000000",
    "quip_ups_count": 42,
    "comments_count": 5,
    "reposts_count": 3
  }
]
```

---

#### `POST /quips` 🔒

Создать quip.

**Request:**
```json
{
  "content": "Тише едешь — дальше будешь",
  "definition": "Спешка вредит делу",
  "usage_examples": "Когда торопишься и делаешь ошибки"
}
```

`definition` и `usage_examples` опциональны.

**Response 201:**
```json
{
  "id": 2,
  "user_id": 1,
  "content": "Тише едешь — дальше будешь",
  "definition": "Спешка вредит делу",
  "usage_examples": "Когда торопишься и делаешь ошибки",
  "created_at": "2026-02-01T16:00:00.000000"
}
```

---

#### `GET /quips/:id`

Получить один quip.

**Response 200:**
```json
{
  "id": 1,
  "user_id": 1,
  "username": "johndoe",
  "content": "Не все то золото, что блестит",
  "definition": "Внешность может быть обманчива",
  "usage_examples": "Когда видишь красивую упаковку",
  "created_at": "2026-02-01T15:30:00.000000",
  "quip_ups_count": 42,
  "comments_count": 5,
  "reposts_count": 3
}
```

**Response 404:**
```json
{"error": "Quip not found"}
```

---

#### `POST /quips/:id/up` 🔒

Лайкнуть quip.

**Response 201:**
```json
{"message": "Upvoted successfully"}
```

**Response 400:**
```json
{"error": "Already upvoted"}
```

---

#### `DELETE /quips/:id/up` 🔒

Убрать лайк.

**Response 200:**
```json
{"message": "Upvote removed successfully"}
```

**Response 400:**
```json
{"error": "Not upvoted"}
```

---

#### `POST /quips/:id/repost` 🔒

Репостнуть quip.

**Response 201:**
```json
{"message": "Reposted successfully"}
```

**Response 400:**
```json
{"error": "Already reposted"}
```

---

### Comments

#### `GET /quips/:id/comments`

Комментарии к quip. Вложенные ответы в поле `replies`.

**Response 200:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "username": "johndoe",
    "content": "Отличная поговорка!",
    "created_at": "2026-02-01T16:30:00.000000",
    "comment_ups_count": 5,
    "replies": [
      {
        "id": 2,
        "user_id": 2,
        "username": "jane",
        "content": "Согласна!",
        "created_at": "2026-02-01T16:35:00.000000",
        "comment_ups_count": 2,
        "replies": []
      }
    ]
  }
]
```

---

#### `POST /quips/:id/comments` 🔒

Добавить комментарий.

**Request:**
```json
{
  "content": "Классная цитата!",
  "parent_id": null
}
```

`parent_id` — ID родительского комментария для ответа (опционально).

**Response 201:**
```json
{
  "id": 3,
  "user_id": 1,
  "quip_id": 1,
  "parent_comment_id": null,
  "content": "Классная цитата!",
  "created_at": "2026-02-01T17:00:00.000000"
}
```

---

#### `POST /quips/comments/:id/up` 🔒

Лайкнуть комментарий.

**Response 201:**
```json
{"message": "Upvoted successfully"}
```

---

#### `DELETE /quips/comments/:id/up` 🔒

Убрать лайк с комментария.

**Response 200:**
```json
{"message": "Upvote removed successfully"}
```

---

### Users

#### `GET /users/:username`

Профиль пользователя со статистикой.

**Response 200:**
```json
{
  "id": 1,
  "username": "johndoe",
  "bio": "Люблю хорошие цитаты",
  "created_at": "2026-02-01T12:00:00.000000",
  "stats": {
    "total_quips": 15,
    "total_quip_ups": 234,
    "total_reposts": 45
  },
  "top_quips": [
    {
      "id": 1,
      "content": "Не все то золото, что блестит",
      "quip_ups_count": 42
    },
    {
      "id": 5,
      "content": "Тише едешь — дальше будешь",
      "quip_ups_count": 38
    }
  ]
}
```

**Response 404:**
```json
{"error": "User not found"}
```

---

#### `GET /users/:username/quips`

Quips пользователя.

**Query params:**
- `page` — номер страницы (default: 1)

**Response 200:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "username": "johndoe",
    "content": "Не все то золото, что блестит",
    "definition": "Внешность может быть обманчива",
    "usage_examples": null,
    "created_at": "2026-02-01T15:30:00.000000",
    "quip_ups_count": 42,
    "comments_count": 5,
    "reposts_count": 3
  }
]
```

---

#### `GET /users/:username/reposts`

Репосты пользователя.

**Query params:**
- `page` — номер страницы (default: 1)

**Response 200:**
```json
[
  {
    "id": 10,
    "user_id": 2,
    "username": "jane",
    "content": "Семь раз отмерь, один раз отрежь",
    "definition": null,
    "usage_examples": null,
    "created_at": "2026-02-01T14:00:00.000000",
    "quip_ups_count": 28,
    "comments_count": 3,
    "reposts_count": 7
  }
]
```

---

## HTTP коды

| Код | Значение |
|-----|----------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

🔒 = требуется `Authorization: Bearer <token>`
