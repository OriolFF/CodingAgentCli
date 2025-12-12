from pydantic import BaseSettings

class Config(BaseSettings):
    DBNAME: str
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str

config = Config()