from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
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