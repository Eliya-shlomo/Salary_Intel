from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    app_name: str = "Salary Intel"
    debug: bool = False

    class Config:
        env_file = (
            "app/.env",      # כשרצים מ-backend/
            "../app/.env",   # fallback
            ".env",          # root .env
            "../.env",       # root fallback
        )

settings = Settings()