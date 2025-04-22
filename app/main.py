from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.endpoints import prompts
from core.config import settings

if os.name == 'nt':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API для получения трендовых промптов с PromptBase с поддержкой кеширования и ограничения частоты запросов",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompts.router)

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в API парсера PromptBase",
        "endpoints": {
            "trending_prompts": "/api/prompts/trending?category={category}",
            "trending_prompts_force_refresh": "/api/prompts/trending?category={category}&force_refresh=true",
            "clear_cache": "/api/prompts/clear-cache?api_key={api_key}"
        },
        "documentation": "/docs",
        "features": [
            "Кеширование результатов для повышения производительности",
            "Ограничение частоты запросов для предотвращения блокировки",
            "Поддержка прокси для обхода блокировок",
            "Ротация User-Agent для имитации различных браузеров"
        ]
    }