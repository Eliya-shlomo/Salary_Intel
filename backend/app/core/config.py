from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str

    # OpenAI
    openai_api_key: str

    # App
    app_name: str = "Salary Intel"
    debug: bool = False

    class Config:
        env_file = "app/.env"

settings = Settings()

