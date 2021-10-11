class Api:
    BASE_PATH = "https://discord.com/api/v9"

    CHANNEL = "/channels/{channelId}"
    CHANNEL_MESSAGES = "/channels/{channelId}/messages"

    GUILD = "/guilds/{guildId}"
    GUILD_MEMBER_ROLE = "/guilds/{guildId}/members/{userId}/roles/{roleId}"
    GUILD_ROLES = "/guilds/{guildId}/roles"
