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
    discord_token: str = Field(..., env="DISCORD_TOKEN")
    guild_ids: Optional[List[int]] = Field(None, env="DISCORD_GUILD_IDS")


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


logging_settings = LoggingSettings()
