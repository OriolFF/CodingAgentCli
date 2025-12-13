from pydantic import BaseSettings

class Settings(BaseSettings):
    example_setting: str = "Example Value"

settings = Settings()