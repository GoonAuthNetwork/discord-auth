import pytest

from dotenv import dotenv_values

from app.clients.discord_api.client import DiscordClient
from app.clients.discord_api.models.channel import CreateMessage


@pytest.fixture
def client() -> DiscordClient:
    env = dotenv_values()
    token = env.get("DISCORD_BOT_TOKEN")

    return DiscordClient(token)


@pytest.mark.asyncio
async def test_get_guild(client: DiscordClient):
    guild_id = 895331501892337754

    guild = await client.get_guild(guild_id)

    assert guild.id == 895331501892337754


@pytest.mark.asyncio
async def test_get_channel(client: DiscordClient):
    channel = await client.get_channel(895331501892337759)

    assert channel is not None
    assert channel.id == 895331501892337759
    assert channel.name == "general"


@pytest.mark.asyncio
async def test_add_role(client: DiscordClient):
    guild = 895331501892337754
    user = 123435280870014976
    role = 896923274070601759

    added = await client.add_guild_member_role(guild, user, role)

    assert added


@pytest.mark.asyncio
async def test_add_remove_roll(client: DiscordClient):
    guild = 895331501892337754
    user = 123435280870014976
    role = 896923274070601759

    added = await client.add_guild_member_role(guild, user, role)

    assert added

    removed = await client.remove_guild_member_role(guild, user, role)

    assert removed


@pytest.mark.asyncio
async def test_create_message(client: DiscordClient):
    channelId = 895853898483511376

    message = CreateMessage(content="Does it work?!")

    messageId = await client.create_message(channelId, message)

    assert messageId is not None
