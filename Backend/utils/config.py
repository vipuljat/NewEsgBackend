from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() # type: ignore    