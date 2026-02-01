# Quiply Backend

Flask + PostgreSQL. JWT auth.

## Запуск

```bash
pip install -r requirements.txt
python init_db.py
python run.py  # :5001
```

## API

Base URL: `/api/v1`

### Health

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/` | Инфо об API |
| GET | `/health` | Статус БД |

### Auth

| Method | Endpoint | Body | Описание |
|--------|----------|------|----------|
| POST | `/auth/register` | `{username, email, password}` | Регистрация |
| POST | `/auth/login` | `{username, password}` | Логин → `{token}` |
| GET | `/auth/me` | — | Текущий юзер (🔒) |

### Quips

| Method | Endpoint | Body | Описание |
|--------|----------|------|----------|
| GET | `/quips` | — | Лента. `?sort=new&page=1` |
| POST | `/quips` | `{content, definition?, usage_examples?}` | Создать (🔒) |
| GET | `/quips/:id` | — | Один quip |
| POST | `/quips/:id/up` | — | Лайк (🔒) |
| DELETE | `/quips/:id/up` | — | Убрать лайк (🔒) |
| POST | `/quips/:id/repost` | — | Репост (🔒) |

### Comments

| Method | Endpoint | Body | Описание |
|--------|----------|------|----------|
| GET | `/quips/:id/comments` | — | Комменты к quip |
| POST | `/quips/:id/comments` | `{content, parent_id?}` | Добавить (🔒) |
| POST | `/quips/comments/:id/up` | — | Лайк коммента (🔒) |
| DELETE | `/quips/comments/:id/up` | — | Убрать лайк (🔒) |

### Users

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/users/:username` | Профиль + статы |
| GET | `/users/:username/quips` | Quips юзера |
| GET | `/users/:username/reposts` | Репосты юзера |

---

🔒 = нужен `Authorization: Bearer <token>`
