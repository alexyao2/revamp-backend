from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database — defaults to local SQLite for development
    DATABASE_URL: str = "sqlite:///./revamp.db"

    # Auth (Supabase JWT secret or your own)
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI Parsing (OpenAI or Anthropic)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Instagram oEmbed (Meta Developer App)
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()