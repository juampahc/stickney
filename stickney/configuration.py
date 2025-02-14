import os
from pydantic_settings import BaseSettings, SettingsConfigDict
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

def get_settings() -> Settings:
    return Settings()
