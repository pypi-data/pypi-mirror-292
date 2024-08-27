from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from onlyaff.api.di import container
from onlyaff.health.api import router as health_router


# Manage the lifespan of the application
@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


# Create the FastAPI application
app = FastAPI(
    title="OnlyAff API Documentation",
    openapi_url="/api-docs/openapi.json",
    docs_url="/api-docs/",
    redoc_url=None,
    lifespan=lifespan,
)

# Auto inject dependencies into the FastAPI request handlers
setup_dishka(container=container, app=app)

# Include all the routers
app.include_router(health_router)
