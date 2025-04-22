import os
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "PromptBase Parser API"

    USE_PROXY: bool = os.getenv("USE_PROXY", "false").lower() == "true"
    PROXY_URL: str = os.getenv("PROXY_URL", "")
    REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", "1.0"))  # Задержка между запросами в секундах

    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "1800"))
    CACHE_SIZE: int = int(os.getenv("CACHE_SIZE", "100"))

    USER_AGENTS: list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    ]
    ROTATE_USER_AGENTS: bool = os.getenv("ROTATE_USER_AGENTS", "true").lower() == "true"

    API_KEY: str = os.getenv("API_KEY", "your-secret-api-key")

    class Config:
        env_file = ".env"


settings = Settings()