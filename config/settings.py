"""Configuration management module."""
import json
import os
from typing import Dict, Any


class Settings:
    """Application settings management."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file {self.config_path}")
    
    @property
    def neis_key(self) -> str:
        """Get NEIS API key."""
        return self._config.get("neisKey", "")
    
    @property
    def cache_days(self) -> int:
        """Get cache expiration days."""
        return self._config.get("cache_day", 7)


# Global settings instance
settings = Settings()