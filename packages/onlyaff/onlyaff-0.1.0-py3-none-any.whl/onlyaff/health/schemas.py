from typing import Literal

from onlyaff.api.schemas import BaseSchema


class Health(BaseSchema):
    status: Literal["ok"] = "ok"
