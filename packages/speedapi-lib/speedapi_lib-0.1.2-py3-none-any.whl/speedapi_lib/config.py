from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class AppConfig(BaseSettings):
    # Speed API Variables
    PUBLISHABLE_KEY: str = Field(..., env='SPEED_PUBLISHABLE_KEY')
    SECRET_KEY: str = Field(..., env='SPEED_SECRET_KEY')
    BASE_URL: str = Field(..., env='SPEED_BASE_URL')

    # Settings for Config class
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
