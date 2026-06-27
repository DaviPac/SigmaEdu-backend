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
    use_formulator_agent: bool = True  # Toggle global para fluxo de 3 agentes (True) vs 2 agentes (False)
    llm_base_url: str = "https://api.openai.com/v1"

    # CORS — valor raw lido do .env como string simples
    allowed_origins_raw: str = "http://localhost:3000"

    model_config = {"env_file": ".env"}

    @property
    def allowed_origins(self) -> List[str]:
        """Converte a string separada por vírgula em lista de origens CORS permitidas."""
        return [origin.strip() for origin in self.allowed_origins_raw.split(",")]

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v


settings = Settings()
