from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter as BaseAPIRouter

from onlyaff.util.typing import inherit_signature_from


class APIRouter(BaseAPIRouter):
    """Custom APIRouter that uses DishkaRoute."""

    @inherit_signature_from(BaseAPIRouter.__init__)
    def __init__(self, *args, **kwargs):
        """Custom APIRouter that uses DishkaRoute."""
        super().__init__(*args, **kwargs, route_class=DishkaRoute)
