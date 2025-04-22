import asyncio
import time
from typing import Dict, Any, Optional


class AsyncCache:

    def __init__(self, max_size: int = 100, ttl: int = 600):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl = ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._data:
                return None

            entry = self._data[key]
            if time.time() > entry['expires']:
                del self._data[key]
                return None

            entry['last_accessed'] = time.time()
            return entry['value']

    async def set(self, key: str, value: Any) -> None:
        current_time = time.time()
        expires = current_time + self._ttl

        async with self._lock:
            if len(self._data) >= self._max_size and key not in self._data:
                self._evict_lru()

            self._data[key] = {
                'value': value,
                'expires': expires,
                'last_accessed': current_time
            }

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()

    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False

    def _evict_lru(self) -> None:
        if not self._data:
            return

        oldest_key = min(self._data.items(), key=lambda x: x[1]['last_accessed'])[0]
        del self._data[oldest_key]

    async def size(self) -> int:
        async with self._lock:
            return len(self._data)
