import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import PydanticBaseSettingsSource
from pathlib import Path
from pydantic import Field
from dotenv import set_key

# Determine the config file location, allowing override via an environment variable.
DEFAULT_ENV_FILE = os.environ.get("CONFIG_FILE", ".env")

class Settings(BaseSettings):
    API_KEY: str = Field(default="helloworld", env="API_KEY")
    MODEL_ID: str = Field(default="Qwen/Qwen2.5-0.5B-Instruct", env="MODEL_ID")
    
    # Define model_config with the env file location and encoding.
    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE, env_file_encoding="utf-8"
    )
    
    def update_config(self, **kwargs):
        """
        Update settings with new values and persist them to the .env file.
        This method:
          - Updates the instance attributes.
          - Writes/updates the key-value pairs in the .env file.
        """
        env_file = self.model_config["env_file"]
        env_file_path = Path(env_file)

        # Ensure the file exists, create it if it doesn't.
        if not env_file_path.exists():
            env_file_path.touch()
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                # Update the settings instance attribute.
                setattr(self, key, value)
                # Persist the updated value to the .env fie
                set_key(env_file, key, str(value))
            else:
                raise ValueError(f"Unknown configuration key: {key}")
            
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Define the sources and their order for loading the settings values.

        Args:
            settings_cls: The Settings class.
            init_settings: The `InitSettingsSource` instance.
            env_settings: The `EnvSettingsSource` instance.
            dotenv_settings: The `DotEnvSettingsSource` instance.
            file_secret_settings: The `SecretsSettingsSource` instance.

        Returns:
            A tuple containing the sources and their order for loading the settings values.
        """
        return init_settings, dotenv_settings, env_settings, file_secret_settings

def get_settings() -> Settings:
    return Settings()
