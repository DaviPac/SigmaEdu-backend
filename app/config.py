from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações globais da aplicação carregadas via .env."""

    database_url: str = "sqlite:///./banco_local.db"
    secret_key: str = "changeme-use-a-real-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env"}

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v) -> List[str]:
        """Converte string separada por vírgula em lista de origens permitidas."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v


settings = Settings()
