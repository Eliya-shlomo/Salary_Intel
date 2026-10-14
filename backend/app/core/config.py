from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    redis_url: str = "redis://localhost:6379"
    api_key: str = Field(min_length=16)
    allowed_origins: str = "http://localhost:3000"
    app_name: str = "Salary Intel"
    debug: bool = False
    port: int = 8000

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    class Config:
        env_file = (
            "app/.env",
            "../app/.env",
            ".env",
            "../.env",
        )

settings = Settings()