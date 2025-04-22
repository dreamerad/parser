from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from services.parser import PromptBaseParser

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("/trending")
async def get_trending_prompts(
        category: str = Query(...,
                              description="Категория промптов: art, logos, graphics, productivity, marketing, photo, games"),
        force_refresh: bool = Query(False,
                                    description="Принудительно обновить кеш, игнорируя существующий"),
        background_tasks: BackgroundTasks = None
):

    valid_categories = ["art", "logos", "graphics", "productivity", "marketing", "photo", "games"]

    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимая категория. Выберите одну из: {', '.join(valid_categories)}"
        )

    parser = PromptBaseParser()
    try:
        if force_refresh and background_tasks:
            try:
                current_data = await parser.get_trending_prompts(category, force_refresh=False)
                # обновление в фоне
                background_tasks.add_task(parser.get_trending_prompts, category, force_refresh=True)
                return {
                    "category": category,
                    "prompts": current_data,
                    "cache_status": "returning_cached_updating_background"
                }
            except Exception:
                pass

        prompts = await parser.get_trending_prompts(category, force_refresh=force_refresh)
        cache_status = "refreshed" if force_refresh else "from_cache_or_new"

        return {
            "category": category,
            "prompts": prompts,
            "cache_status": cache_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")


