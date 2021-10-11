from typing import List
from dispike import Dispike, interactions
from loguru import logger

from app.clients.goon_auth_api import GoonAuthApi
from app.clients.goon_files_api import GoonFilesApi
from app.config import bot_settings, logging_settings
from app.commands import (
    AuthCollection,
    InfoCollection,
    # OptionsCollection,
    SetupCollection,
)
from app.mongodb import connect_to_mongo, close_mongo_connection

logging_settings.setup_loguru()

bot = Dispike(
    client_public_key=bot_settings.discord_public_key,
    application_id=bot_settings.discord_application_id,
    bot_token=bot_settings.discord_bot_token,
)

bot.referenced_application.add_event_handler("startup", connect_to_mongo)
bot.referenced_application.add_event_handler("shutdown", close_mongo_connection)

logger.info(f"Using GoonAuthApi at {bot_settings.awful_auth_address}")
logger.info(f"Using GoonFilesApi at {bot_settings.goon_files_address}")

apis = {
    "auth_api": GoonAuthApi(bot_settings.awful_auth_address, ""),
    "files_api": GoonFilesApi(bot_settings.goon_files_address, ""),
}

collections: List[interactions.EventCollection] = [
    AuthCollection(**apis),
    InfoCollection(**apis),
    # The Dispike models are broken. No options, atleast in this schema, for now
    # OptionsCollection(bot, **apis),
    SetupCollection(**apis),
]

for col in collections:
    bot.register_collection(col)
