from dishka import Provider, Scope, provide

from onlyaff.config.settings import (
    AuthSettings,
    ClerkSettings,
    DatabaseSettings,
    RedisSettings,
)


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_database_settings(self) -> DatabaseSettings:
        return DatabaseSettings()

    @provide
    def get_redis_settings(self) -> RedisSettings:
        return RedisSettings()

    @provide
    def get_auth_settings(self) -> AuthSettings:
        return AuthSettings()

    @provide
    def get_clerk_settings(self) -> ClerkSettings:
        return ClerkSettings()
