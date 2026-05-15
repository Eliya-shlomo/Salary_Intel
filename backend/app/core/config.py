from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    redis_url: str = "redis://localhost:6379"
    api_key: str = "dev-secret-key"  
    app_name: str = "Salary Intel"
    debug: bool = False
    port: int = 8000

    class Config:
        env_file = (
            "app/.env",
            "../app/.env",
            ".env",
            "../.env",
        )

settings = Settings()