import structlog
import logging
from abstract_logger.config_loader import LogConfig


class Logger:
    def __init__(self, config_file_path=None):
        self.config = LogConfig(config_file_path).get_config()
        self.logger = self._configure_logger()

    def _configure_logger(self):
        # Configure basic logging level
        logging.basicConfig(level=self.config["log_level"])

        # Structlog processors
        processors = [
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        # Configure logging type
        if self.config["log_format"] == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        # Configure logging destination
        if self.config["log_destination"] == "file":
            file_handler = logging.FileHandler(self.config["log_file_path"])
            structlog.configure(
                processors=processors,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            logging.getLogger().addHandler(file_handler)
        else:
            structlog.configure(
                processors=processors,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

        return structlog.get_logger()

    def info(self, message, **kwargs):
        self.logger.info(message, **kwargs)

    def debug(self, message, **kwargs):
        self.logger.debug(message, **kwargs)

    def warning(self, message, **kwargs):
        self.logger.warning(message, **kwargs)

    def error(self, message, **kwargs):
        self.logger.error(message, **kwargs)

    def critical(self, message, **kwargs):
        self.logger.critical(message, **kwargs)
