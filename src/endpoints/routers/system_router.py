from fastapi import APIRouter

from endpoints.system_endpoint import HealthData, SystemEndpoint, VersionData

system_routes = APIRouter()


@system_routes.get("/api/goods/health", tags=["System"], operation_id="health")
def health() -> HealthData:
    return SystemEndpoint().health()


@system_routes.get("/api/goods/version", tags=["System"], operation_id="version")
def version() -> VersionData:
    return SystemEndpoint().version()
