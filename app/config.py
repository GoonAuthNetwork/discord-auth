import logging
import os
from pathlib import Path
import sys
from typing import List, Optional
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings, Field

DEVELOPMENT = os.environ.get("development", "False") == "True"

# Only load .env on development
# Production should handle this via docker-compose, etc
if DEVELOPMENT:
    load_dotenv()


class BotSettings(BaseSettings):
    guild_ids: Optional[List[int]] = Field(None, env="DISCORD_GUILD_IDS")

    discord_bot_token: str = Field(..., env="DISCORD_BOT_TOKEN")
    discord_application_id: int = Field(..., env="DISCORD_APPLICATION_ID")
    discord_public_key: str = Field(..., env="DISCORD_PUBLIC_KEY")

    auth_attempt_cache_time: int = Field(300, env="DISCORD_AUTH_ATTEMPT_CACHE_TIME")


bot_settings = BotSettings()


class MongoSettings(BaseSettings):
    min_connections: int = Field(10, env="DB_MIN_CONNECTIONS_COUNT")
    max_connections: int = Field(10, env="DB_MAX_CONNECTIONS_COUNT")

    connection_url: Optional[str] = Field(None, env="DB_CONNECTION_URL")

    mongo_host: str = Field("127.0.0.1", env="DB_MONGO_HOST")
    mongo_port: int = Field(27017, env="DB_MONGO_PORT")
    username: str = Field("root", env="DB_MONGO_USER")
    password: str = Field("password", env="DB_MONGO_PASS")
    database_name: str = Field("discord-auth", env="DB_MONGO_DB_NAME")

    def connection_string(self) -> str:
        if self.connection_url is None:
            return (
                f"mongodb://{self.username}:{self.password}@"
                + "{self.mongo_host}:{self.mongo_port}/"
            )

        return self.connection_url


db_settings = MongoSettings()


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class LoggingSettings(BaseSettings):
    level: str = Field("info", env="LOGGING_LEVEL")
    format: str = Field(
        "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        + "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        env="LOGGING_FORMAT",
    )

    file: bool = Field(False, env="LOGGING_ENABLE_FILE")
    file_path: str = Field("/var/logs", env="LOGGING_FILE_PATH")
    file_name: str = Field("/access.log", env="LOGGING_FILE_NAME")
    file_rotation: str = Field("20 days", env="LOGGING_FILE_ROTATION")
    file_retention: str = Field("1 months", env="LOGGING_FILE_RETENTION")

    def setup_loguru(self):
        # Remove existing
        logger.remove()

        # Add stdout
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=self.level.upper(),
            format=self.format,
        )

        # Add file if desires
        if self.file:
            path = Path.joinpath(self.file_path, self.file_name)
            logger.add(
                str(path),
                rotation=self.file_rotation,
                retention=self.file_retention,
                enqueue=True,
                backtrace=True,
                level=self.level.upper(),
                format=self.format,
            )

        # Intercept logging
        logging.basicConfig(handlers=[InterceptHandler()], level=0)

    def intercept_logging(self, log_name: str):
        _logger = logging.getLogger(log_name)
        _logger.propagate = False
        _logger.handlers = [InterceptHandler()]


logging_settings = LoggingSettings()
