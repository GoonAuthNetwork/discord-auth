import os
import uvicorn

from dispike.creating.models.permissions import (
    ApplicationCommandPermissions,
    ApplicationCommandPermissionType,
    NewApplicationPermission,
)
from loguru import logger

from app.main import bot, bot_settings, collections

# Hardcoded user ids ftw!
user_ids = [
    123435280870014976,  # NotOats
    132205334520397826,  # Tuxide
]

role_ids = [
    895861910199746591,  # Bot Tester @ GDN Hub
]


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

    # Gather commands
    commands = []
    for col in collections:
        commands.extend(col.command_schemas())

    # Global create
    if bot_settings.guild_ids is None:
        logger.info("Creating global discord commands")

        for command in commands:
            bot.register(command=command)

    # Guild create
    else:
        for guild_id in bot_settings.guild_ids:
            logger.info(f"Creating commands on guild (id: {guild_id})")

            for command in commands:
                bot.register(command=command, guild_only=True, guild_to_target=guild_id)


def update_command_permissions():
    user_perms = map(
        lambda id: ApplicationCommandPermissions(
            id=id, type=ApplicationCommandPermissionType.USER, permission=True
        ),
        user_ids,
    )

    group_perms = map(
        lambda id: ApplicationCommandPermissions(
            id=id, type=ApplicationCommandPermissionType.ROLE, permission=True
        ),
        role_ids,
    )

    new_perms = NewApplicationPermission(permissions=[*user_perms, *group_perms])

    # Loop guild ids
    for guild_id in bot_settings.guild_ids:
        logger.info(f"Updating permissions on guild(id: {guild_id})")

        # Pull commands from discord & update them
        for command in bot.get_commands(guild_only=True, guild_id_passed=str(guild_id)):
            bot.set_command_permission(
                command_id=command, guild_id=guild_id, new_permissions=new_perms
            )


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
                bot.delete_command(command)

    # Guild delete
    else:
        for guild_id in bot_settings.guild_ids:
            logger.info(f"Deleting commands on guild (id: {guild_id})")

            for command in bot.get_commands(
                guild_only=True, guild_id_passed=str(guild_id)
            ):
                bot.delete_command(command, guild_only=True, guild_id_passed=guild_id)


# region Utils


def yes_or_no(question: str) -> bool:
    while True:
        reply = str(input(question + " (y/n: )")).lower().strip()
        if reply[:1] == "y":
            return True
        if reply[:1] == "n":
            return False


# endregion
