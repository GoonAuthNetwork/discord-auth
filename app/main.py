from dispike import Dispike

from app.config import bot_settings, logging_settings
from app.commands.goon_auth import AuthCollection
from app.mongodb import connect_to_mongo, close_mongo_connection

logging_settings.setup_loguru()


bot = Dispike(
    client_public_key=bot_settings.discord_public_key,
    application_id=bot_settings.discord_application_id,
    bot_token=bot_settings.discord_bot_token,
)

bot.referenced_application.add_event_handler("startup", connect_to_mongo)
bot.referenced_application.add_event_handler("shutdown", close_mongo_connection)

auth = AuthCollection()
bot.register_collection(collection=auth)
