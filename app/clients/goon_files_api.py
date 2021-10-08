from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from httpx import AsyncClient


class Service(str, Enum):
    DISCORD = "discord"
    OTHER = "other"


class ServiceToken:
    service: Service
    token: str
    info: Optional[str]

    def __init__(self, service: str, token: str, info: Optional[str] = None) -> None:
        self.service = Service(service)
        self.token = token
        self.info = info


class User:
    userId: int
    userName: str
    regDate: datetime
    permaBanned: Optional[datetime]
    services: Optional[List[ServiceToken]]
    createdAt: datetime

    def __init__(
        self,
        userId: int,
        userName: str,
        regDate: datetime,
        createdAt: datetime,
        permaBanned: Optional[datetime] = None,
        services: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self.userId = userId
        self.userName = userName
        self.createdAt = createdAt
        self.permaBanned = permaBanned

        if regDate is not None:
            self.regDate = datetime.fromisoformat(regDate)

        if services is not None:
            self.services = []
            for dict in services:
                self.services.append(ServiceToken(**dict))

    def find_service(self, service: Service) -> Optional[ServiceToken]:
        for serviceToken in self.services:
            if serviceToken.service == service:
                return serviceToken
        return None


class GoonFilesApi:
    def __init__(self, host: str, headers: Dict[str, str] = None) -> None:
        self.client = AsyncClient(base_url=host, headers=headers)

    async def sa_name_for_service(self, service: Service, token: str) -> Optional[str]:
        try:
            user = await self.find_user_by_service(service, token)

            if user is not None:
                return user.userName
        except TypeError:
            pass

        return None

    async def find_user_by_service(
        self, service: Service, token: str
    ) -> Optional[User]:
        payload = {"service": service.value, "token": token}
        response = await self.client.get("/user/", params=payload)

        # This shouldn't happen, but who knows...
        if response.status_code == 422:
            raise TypeError("Invalid query parameter")

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return User(**wrapped)

    async def find_user(self, userId: int) -> Optional[User]:
        response = await self.client.get(f"/user/{userId}")

        # This shouldn't happen, but who knows...
        if response.status_code == 422:
            raise TypeError("Invalid query parameter")

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return User(**wrapped)

    async def create_user(
        self,
        userId: int,
        userName: str,
        regDate: datetime,
        services: Optional[List[ServiceToken]] = None,
    ) -> Optional[User]:
        payload = {
            "userId": userId,
            "userName": userName,
            "regDate": regDate.isoformat(),
        }
        if services is not None:
            payload["services"] = []
            for serviceToken in services:
                serviceTokenDict = {
                    "service": serviceToken.service.value,
                    "token": serviceToken.token,
                }

                if serviceToken.info is not None:
                    serviceTokenDict["info"] = serviceToken.info

                payload["services"].append(serviceTokenDict)

        response = await self.client.post("/user/", json=payload)

        if response.status_code == 422:
            raise TypeError("Invalid user parameter")

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return User(**wrapped)

    async def add_service_token(
        self, userId: int, serviceToken: ServiceToken
    ) -> Optional[User]:
        payload = {"service": serviceToken.service.value, "token": serviceToken.token}
        if serviceToken.info is not None:
            payload["info"] = serviceToken.info

        response = await self.client.put(f"/user/{userId}/service", json=payload)

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            return None

        wrapped = response.json()
        return User(**wrapped)

    async def create_or_update_user(
        self,
        userId: int,
        userName: str,
        regDate: datetime,
        serviceToken: ServiceToken,
    ) -> Optional[User]:
        """Creates or updates a user with the specified serviceToken

        Args:
            userId (int): [description]
            userName (str): [description]
            regDate (datetime): [description]
            serviceToken (ServiceToken): [description]

        Returns:
            Optional[User]: [description]
        """
        user = await self.find_user(userId)
        if user is None:
            # Create
            return await self.create_user(userId, userName, regDate, [serviceToken])
        else:
            # Update
            return await self.add_service_token(userId, serviceToken)
