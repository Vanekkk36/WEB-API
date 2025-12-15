from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://todo_user:your_secure_password_123@postgres:5432/todo_db"
    EXTERNAL_API_URL: str = "https://jsonplaceholder.typicode.com/todos"
    BACKGROUND_TASK_INTERVAL: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()