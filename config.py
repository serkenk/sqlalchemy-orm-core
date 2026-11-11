from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    REDIS_URL: str

    # JWT Authentication Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM Configuration
    OPENAI_API_KEY: str = "mock-key-for-testing"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Ollama Local LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:1.5b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings instance
settings = Settings()
