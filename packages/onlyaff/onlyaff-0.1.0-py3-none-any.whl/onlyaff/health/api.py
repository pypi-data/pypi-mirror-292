from onlyaff.api.core import APIRouter
from onlyaff.health.schemas import Health

router = APIRouter(tags=["Health"], prefix="/health")


@router.get("/", operation_id="GetHealth")
async def get_health() -> Health:
    return Health()
