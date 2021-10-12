# Discord Auth

Discord authentication bot for [Goon Auth Network](https://github.com/GoonAuthNetwork). Currently uses application commands and Discord REST API for authentication.

## Getting Started
### Install dependencies
Install dependencies using poetry:
```
poetry install
```
Read more about [installing poetry](https://python-poetry.org/docs/).

### Configure your environment
Copy the `.env.example` file to `.env`, the following keys must be present:
```
DISCORD_BOT_TOKEN=<discord_bot_token:str>
DISCORD_APPLICATION_ID=<discord_application_id:int>
DISCORD_PUBLIC_KEY=<discord_public_key:str>

AWFUL_AUTH_ADDRESS=<http_address>
GOON_FILES_ADDRESS=<http_address>
```

Please configure the rest of the settings to your liking. The bottom section is setting used for the command registration script and are optional.

### Development
Start the required services:

- [Awful Auth](https://github.com/GoonAuthNetwork/awful-auth) - something awful profile authentication
- [Goon Files](https://github.com/GoonAuthNetwork/goon-files) -  storing authenticated users
- [MongoDB](https://www.mongodb.com/) - storing temporary authentication data and per discord server options


Start a poetry shell, register commands, and start the application
```
poetry shell
poe create_commands
poe start
```

## FAQ

### Why aren't my commands showing up?
Register commands globally `poe create_commands global` or ensure `DISCORD_GUILD_IDS` is set. When registering globally discord can take [up to 1 hour](https://discord.com/developers/docs/interactions/application-commands#registering-a-command) for the commands to display.