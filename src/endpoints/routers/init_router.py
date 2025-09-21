from app_init import app
from endpoints.routers.groups_router import groups_routes
from endpoints.routers.system_router import system_routes

app.include_router(system_routes)
app.include_router(groups_routes)