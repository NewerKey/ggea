from functools import lru_cache

import decouple

from src.config.settings.base import Settings
from src.config.settings.environment import Environment


class SettingsFactory:
    def __init__(self, environment: str):
        self.environment = environment

    def __call__(self) -> Settings:
        # Imports in code to avoid "decouple.UndefinedValueError: ENV_VARIABLE not found."
        # If a setting is imported all the variables which are decoupled need to be defined in the environment
        # Other solution would be to provide a default value for each variable
        # Doing it this way is more explicit and easier to debug

        if self.environment == Environment.DEVELOPMENT.value:
            from src.config.settings.development import DevelopmentSettings

            return DevelopmentSettings()
        elif self.environment == Environment.STAGING.value:
            from src.config.settings.staging import StagingSettings

            return StagingSettings()
        elif self.environment == Environment.PRODUCTION.value:
            from src.config.settings.production import ProductionSettings

            return ProductionSettings()
        else:
            raise ValueError(f"Invalid environment: {self.environment}")


@lru_cache()
def get_settings() -> Settings:
    return SettingsFactory(environment=decouple.config("ENVIRONMENT", default="DEV", cast=str))()  # type: ignore


settings: Settings = get_settings()
