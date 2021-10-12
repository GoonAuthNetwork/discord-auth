import os
import sys
from typing import Any, List, Optional

import uvicorn
from dispike.creating.models.permissions import (
    ApplicationCommandPermissions,
    ApplicationCommandPermissionType,
    NewApplicationPermission,
)
from loguru import logger
from pydantic import BaseSettings, Field

from app.main import bot, collections


class DevSettings(BaseSettings):
    guild_ids: Optional[List[int]] = Field(None, env="DISCORD_GUILD_IDS")
    role_ids: Optional[List[int]] = Field(None, env="DISCORD_ROLE_ID")
    user_ids: Optional[List[int]] = Field(None, env="DISCORD_USER_IDS")


settings = DevSettings(_env_file=".env")


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

    # Global context
    if _is_global_context():
        logger.info("SCRIPT: Creating global discord commands")

        [bot.register(cmd) for cmd in _get_commands()]

    elif settings.guild_ids is not None:
        for guild_id in settings.guild_ids:
            logger.info(f"SCRIPT: Creating commands for guild {guild_id}")

            for cmd in _get_commands():
                bot.register(command=cmd, guild_only=True, guild_to_target=guild_id)
    else:
        logger.warning(
            "SCRIPT: Failed to create commands. No global context or guild ids."
        )


def update_command_permissions():
    user_perms = map(
        lambda id: ApplicationCommandPermissions(
            id=id, type=ApplicationCommandPermissionType.USER, permission=True
        ),
        settings.user_ids,
    )

    group_perms = map(
        lambda id: ApplicationCommandPermissions(
            id=id, type=ApplicationCommandPermissionType.ROLE, permission=True
        ),
        settings.role_ids,
    )

    permissions = NewApplicationPermission(permissions=[*user_perms, *group_perms])

    if _is_global_context():
        # Currently no support via Dispike for global command permissions
        logger.warning("SCRIPT: There's no support for global command permissions.")

    elif settings.guild_ids is not None:
        for guild_id in settings.guild_ids:
            logger.info(f"SCRIPT: Creating commands for guild {guild_id}")

            for cmd in _get_existing_commands(guild_id):
                bot.set_command_permission(cmd, guild_id, permissions)

    else:
        logger.warning(
            "SCRIPT: Failed to update permissions. No global context or guild ids."
        )


def delete_commands():
    """Deletes every registered command on discord"""

    if _is_global_context():
        logger.info("SCRIPT: Deleting global discord commands")
        logger.warning(
            "This will remove _all_ commands associated "
            "with this application on _every_ server."
        )

        if _yes_or_no("Confirm deletion"):
            [bot.delete_command(cmd) for cmd in _get_existing_commands()]

    elif settings.guild_ids is not None:
        for guild_id in settings.guild_ids:
            logger.info(f"SCRIPT: Deleting commands for {guild_id}")

            for cmd in _get_existing_commands(guild_id):
                bot.delete_command(cmd, guild_only=True, guild_id_passed=guild_id)
    else:
        logger.warning(
            "SCRIPT: Failed to update permissions. No global context or guild ids."
        )


# region Utils


def _is_global_context() -> bool:
    return True if "global" in sys.argv else False


def _get_commands() -> List[Any]:
    commands = []

    for collection in collections:
        commands.extend(collection.command_schemas())

    return commands


def _get_existing_commands(guild_id: Optional[int] = None) -> List[Any]:
    if guild_id is not None:
        return bot.get_commands(guild_only=True, guild_id_passed=str(guild_id))

    return bot.get_commands()


def _yes_or_no(question: str) -> bool:
    while True:
        reply = str(input(question + " (y/n: )")).lower().strip()
        if reply[:1] == "y":
            return True
        if reply[:1] == "n":
            return False


# endregion
