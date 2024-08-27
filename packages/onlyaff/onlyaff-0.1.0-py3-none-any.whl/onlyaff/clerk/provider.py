from collections.abc import AsyncGenerator

from clerk_backend_sdk.api_client import ApiClient
from clerk_backend_sdk.configuration import Configuration
from dishka import Provider, Scope, provide

from onlyaff.clerk.service import ClerkService
from onlyaff.config.settings import ClerkSettings


class ClerkProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_clerk_client(
        self, settings: ClerkSettings
    ) -> AsyncGenerator[ApiClient, None]:
        configuration = Configuration(
            host=settings.CLERK_BACKEND_API_URL.unicode_host(),
            access_token=settings.CLERK_BACKEND_API_KEY,
        )
        
        async with ApiClient(configuration) as client:
            yield client

    @provide
    async def get_clerk_service(self, client: ApiClient):
        return ClerkService(client=client)
