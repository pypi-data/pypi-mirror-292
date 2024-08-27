from dishka import make_async_container

from onlyaff.clerk.provider import ClerkProvider
from onlyaff.config.provider import ConfigProvider

container = make_async_container(ConfigProvider(), ClerkProvider())
