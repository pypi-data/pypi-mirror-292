import os
from functools import lru_cache

from loguru import logger
from neat.types import LLMModels
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

STRUCTURED_OUTPUT_MODELS = ["gpt-4o-mini", "gpt-4o"]
UNSUPPORTED_TOOL_MODELS = ("command-r", "command-r-plus")


class Settings(BaseSettings):
    db_file: str = Field(default="prompt_versions.db", description="Database file path")
    default_model: LLMModels = Field(
        default="mistral/mistral-large-latest", description="Default LLM model"
    )
    default_temperature: float = Field(
        default=0.7, description="Default temperature for LLM"
    )
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    cohere_api_key: str = ""
    mistral_api_key: str = ""

    log_level: str = Field(default="DEBUG", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


@lru_cache()
def get_settings(**kwargs) -> Settings:
    """
    Get settings. ready for FastAPI's Depends.
    lru_cache - cache the Settings object per arguments given.
    """
    # logger.debug("Getting settings")
    settings = Settings(**kwargs)
    return settings


settings: Settings = get_settings()
os.environ["OPENAI_API_KEY"] = settings.openai_api_key
os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
os.environ["COHERE_API_KEY"] = settings.cohere_api_key
os.environ["MISTRAL_API_KEY"] = settings.mistral_api_key


def setup_logging(log_level: str):
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg),
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )


setup_logging(settings.log_level)
