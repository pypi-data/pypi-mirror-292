import os
import json

class LogConfig:
   # Automatically invoked when you create an object of LogConfig class
    def __init__(self, config_file_path=None):
        self.config_file_path = config_file_path or os.getenv("LOG_CONFIG_PATH", "log_config.json")
        self.config = self._load_config()

    def _load_config(self):
        # Load configuration from the provided JSON file path
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, "r") as file:
                config = json.load(file)
        else:
            config = {}

        # Override with environment variables if they exist
        config["log_level"] = os.getenv("LOG_LEVEL", config.get("log_level", "INFO"))
        config["log_destination"] = os.getenv("LOG_DESTINATION", config.get("log_destination", "console"))
        config["log_file_path"] = os.getenv("LOG_FILE_PATH", config.get("log_file_path", "app.log"))
        config["log_format"] = os.getenv("LOG_FORMAT", config.get("log_format", "json"))

        return config

    def get_config(self):
        return self.config
