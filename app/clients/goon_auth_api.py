from datetime import datetime
from typing import Dict, Optional
from httpx import AsyncClient


class GoonAuthChallenge:
    user_name: str
    hash: str

    def __init__(self, user_name: str, hash: str) -> None:
        self.user_name = user_name
        self.hash = hash


class GoonAuthStatus:
    validated: bool
    user_name: str
    user_id: int
    register_date: datetime
    permabanned: Optional[datetime]

    def __init__(
        self,
        validated: bool,
        user_name: Optional[str] = None,
        user_id: Optional[int] = None,
        register_date: Optional[str] = None,
        permabanned: Optional[str] = None,
    ) -> None:
        self.validated = validated
        self.user_name = user_name
        self.user_id = user_id

        if register_date is not None:
            self.register_date = datetime.fromisoformat(register_date)

        if permabanned is not None:
            self.permabanned = datetime.fromisoformat(permabanned)


class GoonAuthApi:
    def __init__(self, host: str, headers: Dict[str, str] = None) -> None:
        self.client = AsyncClient(base_url=host, headers=headers)

    async def get_verification(self, user_name: str) -> Optional[GoonAuthChallenge]:
        payload = {"user_name": user_name}
        response = await self.client.get("/goon_auth/verification", params=payload)

        # Should only see this from username issues
        if response.status_code == 422:
            raise TypeError("Invalid username")

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return GoonAuthChallenge(**wrapped)

    async def get_verification_update(self, user_name: str) -> Optional[GoonAuthStatus]:
        payload = {"user_name": user_name}
        response = await self.client.get(
            "/goon_auth/verification/update", params=payload
        )

        # Unknown hash
        if response.status_code == 404 and "message" in response.json():
            raise ValueError("Unknown hash for supplied username")

        # Should only see this from username issues
        if response.status_code == 422:
            raise TypeError("Invalid username")

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return GoonAuthStatus(**wrapped)
