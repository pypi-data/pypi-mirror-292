"""
Configuration file for the auth module
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class AuthConfig(BaseSettings):
    """
    Configuration class for the auth module
    """
    model_config: ConfigDict = ConfigDict(
        env_file=".env" if not os.getenv("SECRET_KEY") else None
    )
    secret_key: str = os.getenv("SECRET_KEY")


@lru_cache()
def get_auth_config() -> AuthConfig:
    """
    Get the configuration for the auth module
    """
    return AuthConfig()
