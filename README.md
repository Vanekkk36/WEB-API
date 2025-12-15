# TODO API + WebSocket + Фоновая задача

## Описание проекта

Проект представляет собой REST API сервис для управления задачами (TODO-list) со следующими возможностями:

- **REST API** - полный CRUD для управления задачами
- **WebSocket** - реальное время уведомления о изменениях задач
- **Фоновая задача** - автоматическое наполнение базы данных задачами из внешнего API
- **Асинхронная работа с БД** - использование async/await для всех операций с базой данных

##  Функциональность

### REST API для управления задачами

Проект реализует все требуемые эндпоинты:

- ✅ `GET /tasks` - получение списка задач
- ✅ `GET /tasks/{id}` - получение задачи по ID
- ✅ `POST /tasks` - создание новой задачи
- ✅ `PATCH /tasks/{id}` - частичное обновление задачи
- ✅ `DELETE /tasks/{id}` - удаление задачи
- ✅ `POST /task-generator/run` - принудительный запуск фоновой задачи

### WebSocket уведомления

- ✅ WebSocket эндпоинт `/ws/tasks` для уведомлений в реальном времени
- ✅ Автоматическая отправка уведомлений при создании, обновлении и удалении задач
- ✅ Уведомления о завершении фоновой задачи

### Фоновая задача

- ✅ Автоматический запуск при старте приложения
- ✅ Периодическое получение данных со стороннего API (jsonplaceholder.typicode.com)
- ✅ Сохранение полученных задач в базу данных
- ✅ Возможность принудительного запуска через HTTP запрос

### Асинхронная работа с БД

- ✅ Все операции с базой данных выполняются асинхронно
- ✅ Использование `AsyncSession` из SQLAlchemy
- ✅ Оптимизированные запросы с использованием async/await

### Эндпоинты

#### GET /tasks
Получить список задач с пагинацией.

**Параметры запроса:**
- `skip` (int, опционально) - количество пропускаемых записей (по умолчанию: 0)
- `limit` (int, опционально) - максимальное количество записей (по умолчанию: 100)

**Пример запроса:**
```bash
curl http://localhost:8000/tasks?skip=0&limit=10
```

**Пример ответа:**
```json
[
  {
    "id": 1,
    "title": "delectus aut autem",
    "description": "From external API: User 1",
    "completed": false,
    "created_at": "2025-12-15T12:00:31.168401Z",
    "updated_at": null
  }
]
```

#### GET /tasks/{id}
Получить задачу по ID.

**Пример запроса:**
```bash
curl http://localhost:8000/tasks/1
```

#### POST /tasks
Создать новую задачу.

**Тело запроса:**
```json
{
  "title": "Новая задача",
  "description": "Описание задачи",
  "completed": false
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Новая задача", "description": "Описание", "completed": false}'
```

#### PATCH /tasks/{id}
Частично обновить задачу. Все поля опциональны.

**Тело запроса:**
```json
{
  "title": "Обновленный заголовок",
  "completed": true
}
```

**Пример запроса:**
```bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

#### DELETE /tasks/{id}
Удалить задачу.

**Пример запроса:**
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

**Ответ:** 204 No Content

#### POST /task-generator/run
Принудительно запустить фоновую задачу для получения задач со стороннего API.

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/task-generator/run
```

**Пример ответа:**
```json
{
  "message": "Background task executed successfully",
  "tasks_created": 200
}
```

#### GET /health
Проверка здоровья приложения.

**Пример запроса:**
```bash
curl http://localhost:8000/health
```

**Пример ответа:**
```json
{
  "status": "healthy"
}
```

## WebSocket

### Подключение

WebSocket эндпоинт доступен по адресу: `ws://localhost:8000/ws/tasks`

### Использование тестового клиента

В проекте включен простой WebSocket клиент для тестирования:

```bash
python websocket_client.py
```

### Типы сообщений

После подключения клиент получает уведомления о следующих событиях:

1. **task_created** - создана новая задача
```json
{
  "type": "task_created",
  "data": {
    "task": {
      "id": 1,
      "title": "Новая задача",
      "description": "Описание",
      "completed": false,
      "created_at": "2025-12-15T12:00:31.168401Z"
    }
  }
}
```

2. **task_updated** - задача обновлена
```json
{
  "type": "task_updated",
  "data": {
    "task": {
      "id": 1,
      "title": "Обновленная задача",
      "completed": true
    }
  }
}
```

3. **task_deleted** - задача удалена
```json
{
  "type": "task_deleted",
  "data": {
    "task_id": 1
  }
}
```

4. **background_task_completed** - фоновая задача завершена
```json
{
  "type": "background_task_completed",
  "data": {
    "created_count": 200
  }
}
```

## Фоновая задача

### Автоматический запуск

Фоновая задача автоматически запускается при старте приложения и работает в фоновом режиме. Она:

1. Получает задачи со стороннего API (jsonplaceholder.typicode.com/todos)
2. Преобразует их в формат базы данных
3. Сохраняет в PostgreSQL
4. Повторяет процесс каждые `BACKGROUND_TASK_INTERVAL` секунд (по умолчанию 300 секунд = 5 минут)

```

### Логирование

Все операции фоновой задачи логируются:
- Запуск задачи
- Количество полученных задач
- Ошибки при получении или сохранении данных

## Структура проекта
```
```
todo_api/
├── api/
│   └── endpoints.py          # REST API эндпоинты
├── main.py                   # Главный файл приложения
├── database.py               # Конфигурация базы данных
├── models.py                 # SQLAlchemy модели
├── schemas.py                # Pydantic схемы для валидации
├── crud.py                   # CRUD операции
├── background_tasks.py       # Фоновая задача
├── websocket.py              # WebSocket менеджер
├── websocket_client.py       # Тестовый WebSocket клиент
├── config.py                 # Конфигурация приложения
├── requirements.txt          # Зависимости Python
├── Dockerfile                # Docker образ приложения
├── docker-compose.yml        # Docker Compose конфигурация
└── README.md                 # Документация
```

### Описание файлов

- **main.py** - точка входа приложения, настройка FastAPI, WebSocket эндпоинт, lifecycle управление
- **api/endpoints.py** - все REST API эндпоинты
- **database.py** - настройка асинхронного движка SQLAlchemy и сессий
- **models.py** - модель Task для базы данных
- **schemas.py** - Pydantic схемы для валидации входных/выходных данных
- **crud.py** - класс с методами для работы с базой данных (CRUD операции)
- **background_tasks.py** - класс BackgroundTask для периодического получения данных
- **websocket.py** - ConnectionManager для управления WebSocket подключениями
- **config.py** - настройки приложения через Pydantic Settings


## Модель данных

### Task

Таблица `tasks` содержит следующие поля:

- `id` (Integer, Primary Key) - уникальный идентификатор
- `title` (String, Required) - название задачи
- `description` (String, Optional) - описание задачи
- `completed` (Boolean, Default: False) - статус выполнения
- `created_at` (DateTime, Auto) - дата создания
- `updated_at` (DateTime, Auto) - дата последнего обновления

## ✅ Соответствие требованиям

Проект полностью соответствует всем требованиям задания:

- ✅ REST API для управления списком задач (TODO-list)
  - ✅ GET /tasks - список задач
  - ✅ GET /tasks/{id} - получить задачу
  - ✅ POST /tasks - создать
  - ✅ PATCH /tasks/{id} - частичное обновление
  - ✅ DELETE /tasks/{id} - удалить
  - ✅ POST /task-generator/run - принудительно вызвать фоновую задачу

- ✅ WebSocket-канал для уведомлений клиентов в реальном времени
  - ✅ /ws/tasks

- ✅ Фоновая задача, которая периодически наполняет базу данных данными полученными по httpx со стороннего сайта

- ✅ Возможность принудительного запуска фоновой задачи по HTTP-запросу

- ✅ Задействована асинхронная работа с базой данных