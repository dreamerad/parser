import asyncio
import json
import random
import time
from typing import List, Dict, Any

import aiohttp
from bs4 import BeautifulSoup

from core.config import settings
from utils.cache import AsyncCache


class PromptBaseParser:
    BASE_URL = "https://promptbase.com"

    CATEGORY_URLS = {
        "art": "/art-and-illustrations",
        "logos": "/logos-and-icons",
        "graphics": "/graphics-and-design",
        "productivity": "/productivity-and-writing",
        "marketing": "/marketing-and-business",
        "photo": "/photography",
        "games": "/games-and-3d"
    }

    _cache = AsyncCache(max_size=settings.CACHE_SIZE, ttl=settings.CACHE_TTL)
    _last_request_time = 0

    async def get_trending_prompts(self, category: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        if category not in self.CATEGORY_URLS:
            raise ValueError(f"Неизвестная категория: {category}")

        cache_key = f"trending_prompts_{category}"
        if not force_refresh:
            cached_data = await self._cache.get(cache_key)
            if cached_data:
                print(f"[INFO] Используются кешированные данные для категории {category}")
                return cached_data

        # ограничение частоты запросов
        await self._apply_rate_limit()

        category_url = f"{self.BASE_URL}{self.CATEGORY_URLS[category]}"
        print(f"[INFO] Запрос URL: {category_url}")

        # выбираем User-Agent
        user_agent = settings.USER_AGENTS[0]
        if settings.ROTATE_USER_AGENTS:
            user_agent = random.choice(settings.USER_AGENTS)

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }

        try:
            proxy = settings.PROXY_URL if settings.USE_PROXY else None

            async with aiohttp.ClientSession() as session:
                PromptBaseParser._last_request_time = time.time()

                async with session.get(category_url, headers=headers, proxy=proxy) as response:
                    print(f"[INFO] Статус ответа: {response.status}")
                    if response.status != 200:
                        raise Exception(f"Ошибка при запросе: {response.status}")

                    html = await response.text()
                    print(f"[INFO] Получен HTML размером: {len(html)} символов")

            prompts = await self._parse_html(html, category)
            print(f"[INFO] Результат парсинга: {len(prompts)} промптов")

            await self._cache.set(cache_key, prompts)

            return prompts
        except Exception as e:
            print(f"[ERROR] Общая ошибка в get_trending_prompts: {str(e)}")
            cached_data = await self._cache.get(cache_key)
            if cached_data:
                print(f"[INFO] Используются кешированные данные после ошибки для категории {category}")
                return cached_data
            raise

    async def _apply_rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - PromptBaseParser._last_request_time

        if time_since_last_request < settings.REQUEST_DELAY:
            delay = settings.REQUEST_DELAY - time_since_last_request
            print(f"[INFO] Применение задержки {delay:.2f} сек для ограничения частоты запросов")
            await asyncio.sleep(delay)

    async def _parse_html(self, html: str, category: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'lxml')
        prompts = []

        try:
            print(f"[INFO] Начало парсинга HTML для категории {category}")

            script_data = None
            for script in soup.find_all('script'):
                if script.get('id') == 'ng-state':
                    script_data = script.string
                    break

            if script_data:
                try:
                    json_data = json.loads(script_data)
                    trending_data = None

                    if "Trending Prompts" in json_data:
                        trending_data = json_data["Trending Prompts"]
                        print(f"[INFO] Найден ключ 'Trending Prompts'")
                    else:
                        for key in json_data.keys():
                            if "Trending" in key and category in key:
                                trending_data = json_data[key]
                                print(f"[INFO] Найден ключ '{key}'")
                                break

                        if not trending_data:
                            for key in json_data.keys():
                                if "Trending" in key:
                                    trending_data = json_data[key]
                                    print(f"[INFO] Найден ключ '{key}'")
                                    break

                    if trending_data and isinstance(trending_data, list):
                        for item_group in trending_data:
                            if isinstance(item_group, list):
                                for prompt in item_group:
                                    if isinstance(prompt, dict):
                                        prompt_data = self._extract_prompt_data(prompt)
                                        if prompt_data:
                                            prompts.append(prompt_data)
                            elif isinstance(item_group, dict):
                                prompt_data = self._extract_prompt_data(item_group)
                                if prompt_data:
                                    prompts.append(prompt_data)

                except json.JSONDecodeError as json_error:
                    print(f"[ERROR] Ошибка декодирования JSON: {str(json_error)}")
                except Exception as json_error:
                    print(f"[ERROR] Ошибка при обработке JSON данных: {str(json_error)}")
            else:
                print("[WARN] Скрипт ng-state не найден")

        except Exception as e:
            print(f"[ERROR] Общая ошибка при парсинге: {str(e)}")

        return prompts

    def _extract_prompt_data(self, prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(prompt_dict, dict):
            return None

        stats = {
            "views": prompt_dict.get("views", 0),
            "downloads": prompt_dict.get("downloads", 0),
            "favorites": prompt_dict.get("favorites", 0),
            "rating": prompt_dict.get("rating", 0.0),
            "sales": prompt_dict.get("sales", 0)
        }

        prompt_data = {
            "price": prompt_dict.get("price", 0.0),
            "description": prompt_dict.get("title", ""),
            "statistics": stats
        }

        image = prompt_dict.get("image", "")
        if image:
            prompt_data["preview_url"] = image

        return prompt_data
