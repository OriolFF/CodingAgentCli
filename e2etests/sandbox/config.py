from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALLOWED_HOSTS: list[str] = ["localhost", "example.com"]
    DATABASE_URI: str = "sqlite:///./db.sqlite3"
    MODEL_NAMESPACE: str = "model."

settings = Settings()