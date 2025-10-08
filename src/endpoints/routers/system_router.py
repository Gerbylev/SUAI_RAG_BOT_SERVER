from fastapi import APIRouter

from endpoints.models.health_data import HealthData
from endpoints.models.version_data import VersionData
from endpoints.system_endpoint import health_endpoint, version_endpoint

system_routes = APIRouter()


@system_routes.get("/api/goods/health", tags=["System"], operation_id="health")
def health() -> HealthData:
    return health_endpoint()


@system_routes.get("/api/goods/version", tags=["System"], operation_id="version")
def version() -> VersionData:
    return version_endpoint()
