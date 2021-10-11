from pydantic import BaseModel


class Guild(BaseModel):
    id: int
    owner_id: int
