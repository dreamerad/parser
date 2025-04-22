# Promptbase Trending Prompts API

API для получения трендовых промптов с сайта promptbase.com по различным категориям.

## Особенности

- Получение трендовых промптов по категориям (art, logos, raphics, productivity, marketing, photo, games)
- Детальная информация о промптах, включая цену, статистику и описание
- Автоматическое кеширование результатов для повышения производительности
- Ограничение частоты запросов для предотвращения блокировки
- Полная документация API

### Запуск с помощью Docker

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/dreamerad/parser.git
   cd parser
   ```

2. Запустите контейнер с помощью Docker Compose:
   ```bash
   docker-compose up --build
   ```

Сервер будет доступен по адресу http://localhost:8000

## Использование API
## Получение трендовых промптов по категории

```
GET /api/prompts/trending?category=photo
```

Параметры:
- `category` (обязательный): Категория промптов (Art, Logos, Graphics, Productivity, Marketing, Photo, Games)

## Документация
```
GET /docs
GET /redoc
```
