from typing import Any, Dict, List, Optional, Union

from dispike.creating.allowed_mentions import AllowedMentions
from dispike.creating.components import Button, LinkButton, SelectMenu
from dispike.helper import Embed

from pydantic import BaseModel


class Channel(BaseModel):
    id: int
    name: str


class CreateMessage:
    content: Optional[str]
    embeds: Optional[List[Embed]]
    components: Optional[List[Union[Button, LinkButton, SelectMenu]]]
    allowed_mentions: Optional[AllowedMentions]

    def __init__(
        self,
        content: Optional[str] = None,
        embeds: Optional[List[Embed]] = None,
        components: Optional[List[Union[Button, LinkButton, SelectMenu]]] = None,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> None:
        if content is None and embeds is None:
            raise TypeError("Either content or embeds must be present")

        self.content = content
        self.embeds = embeds
        self.components = components
        self.allowed_mentions = allowed_mentions

    def request_data(self) -> Dict[str, Any]:
        response = dict()

        if self.content is not None:
            response["content"] = self.content

        if self.embeds is not None:
            response["embeds"] = []
            for embed in self.embeds:
                response["embeds"].append(embed.to_dict())

        if self.components is not None:
            response["components"] = []
            for component in self.components:
                response["components"].append(component.to_dict())

        if self.allowed_mentions is not None:
            response["allowed_mentions"] = self.allowed_mentions.dict()

        return response
