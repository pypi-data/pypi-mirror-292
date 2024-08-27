from clerk_backend_sdk import (
    ActorTokensApi,
    ApiClient,
)
from pydantic.dataclasses import dataclass


@dataclass
class ClerkService:
    client: ApiClient

    async def get_user(self, user_id: str):
        api = ActorTokensApi(self.client)
