import unittest

from src.config.setup import settings
from src.config.settings.base import Settings
from src.config.settings.development import DevelopmentSettings
from src.config.settings.production import ProductionSettings
from src.config.settings.staging import StagingSettings
from src.config.settings.environment import Environment


class TestAppSettings(unittest.TestCase):
    def setUp(self) -> None:
        self.base_settings = Settings()
        self.dev_settings = DevelopmentSettings()
        self.prod_settings = ProductionSettings()
        self.stage_settings = StagingSettings()
        self.app_env = Environment
        self.default_settings = settings

    def test_enum_env_provide_3_environments(self) -> None:
        assert self.app_env.DEVELOPMENT.value == "DEV"
        assert self.app_env.PRODUCTION.value == "PROD"
        assert self.app_env.STAGING.value == "STAGE"

    def test_settings_environment_is_enum_environment(self) -> None:
        assert isinstance(self.dev_settings.ENVIRONMENT, Environment)
        assert isinstance(self.prod_settings.ENVIRONMENT, Environment)
        assert isinstance(self.stage_settings.ENVIRONMENT, Environment)

    def test_settings_environment_controlled_by_dotenv_environment_variable(self) -> None:
        env_var_dev = self.default_settings.ENVIRONMENT == self.app_env.DEVELOPMENT
        env_var_prod = self.default_settings.ENVIRONMENT == self.app_env.PRODUCTION
        env_var_stage = self.default_settings.ENVIRONMENT == self.app_env.STAGING
        assert env_var_dev or env_var_prod or env_var_stage

    def test_default_settings_is_dev_settings(self) -> None:
        assert isinstance(self.default_settings, Settings)

    def test_settings_fastapi_instance_attributes(self) -> None:
        expected_attributes = {
            "title": "Gotta Guess Em All!",
            "version": "0.1.0",
            "debug": self.default_settings.DEBUG,
            "description": self.default_settings.DESCRIPTION,
            "docs_url": "/docs",
            "openapi_url": "/openapi.json",
            "redoc_url": "/redoc",
            "openapi_prefix": "",
            "api_prefix": "/api"
        }

        assert  self.default_settings.set_backend_app_attributes == expected_attributes

    def tearDown(self) -> None:
        pass
