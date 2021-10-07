import os
import uvicorn

from dispike.incoming.incoming_interactions import IncomingApplicationCommand
from loguru import logger

# TODO: Automatic listing of collections (auth), probably by __init__.py file
from app.main import auth, bot, bot_settings


def start():
    """Laucnhes the application via uvicorn"""
    reload_dir = os.path.join(os.getcwd(), "./app")
    logger.info("Starting Discord Auth")
    logger.info(f"Auto reloading from: {reload_dir}")

    uvicorn.run(
        "app.main:bot.referenced_application",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_dirs=[reload_dir],
    )


def create_commands():
    """Create (or updates) all the registered commands on discord"""

    # Global create
    if bot_settings.guild_ids is None:
        logger.info("Creating global discord commands")

        for command in auth.command_schemas():
            register_command(command)

    # Guild create
    else:
        commands = auth.command_schemas()

        for guild_id in bot_settings.guild_ids:
            logger.info(f"Creating commands on guild (id: {guild_id})")

            for command in commands:
                register_command(command, guild_id)


def delete_commands():
    """Deletes every registered command on discord"""

    # Global delete
    if bot_settings.guild_ids is None:
        logger.info("Deleting all commands globally")
        logger.warning(
            "This will remove _all_ commands associated "
            "with this application on _every_ server."
        )

        if yes_or_no("Confirm deletion"):
            # Hope you like waiting an hour for global commands to refresh!
            for command in bot.get_commands():
                delete_command(command)

    # Guild delete
    else:
        for guild_id in bot_settings.guild_ids:
            logger.info(f"Deleting commands on guild (id: {guild_id})")

            for command in bot.get_commands(
                guild_only=True, guild_id_passed=str(guild_id)
            ):
                delete_command(command, guild_id)


# region Utils


def register_command(command: IncomingApplicationCommand, guild_id: int = None):
    if guild_id is None:
        bot.register(command=command)
    else:
        bot.register(command=command, guild_only=True, guild_to_target=guild_id)


def delete_command(command: IncomingApplicationCommand, guild_id: int = None):
    if guild_id is None:
        bot.delete_command(command)
    else:
        bot.delete_command(command, guild_only=True, guild_id_passed=guild_id)


def yes_or_no(question: str) -> bool:
    while True:
        reply = str(input(question + " (y/n: )")).lower().strip()
        if reply[:1] == "y":
            return True
        if reply[:1] == "n":
            return False


# endregion
