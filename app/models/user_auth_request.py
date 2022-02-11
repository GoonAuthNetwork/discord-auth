import odmantic
from datetime import datetime


class UserAuthRequest(odmantic.Model):
    userDiscordId: int = odmantic.Field(..., title="The user's discord id")

    saName: str = odmantic.Field(
        ...,
        title="The user's SA Username",
        min_length=3,
        # TODO: Reimplement validation once userid api is added.
        # Thanks SA for having absolutely no standards for valid usernames.
        # max_length=50,
        # regex=r"^[\w\-\_\ ]+$",
    )

    challengeHash: str = odmantic.Field(
        ..., title="Challenge hash for the user's profile"
    )

    lastUpdated: datetime = odmantic.Field(default_factory=datetime.now)

    # def configure_index(engine: odmantic.AIOEngine) -> None:
    #    collection = engine.get_collection(UserAuthRequest)
    #    collection.create_index(
    #        "lastUpdated",
    #        expireAfterSeconds=(bot_settings.auth_attempt_lifespan * 60),
    #    )
