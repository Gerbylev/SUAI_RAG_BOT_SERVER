from typing import List

from fastapi import APIRouter, HTTPException

from endpoints.groups_endpoint import GroupsEndpoint
from endpoints.models.test_data import TestRequest

groups_routes = APIRouter()


@groups_routes.post("/api/groups", tags=["Groups"], operation_id="create_group")
async def create_group(request: TestRequest) -> dict:
    try:
        return await GroupsEndpoint().create_group(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@groups_routes.get("/api/groups/{group_id}", tags=["Groups"], operation_id="get_group")
async def get_group(group_id: int) -> dict:
    result = await GroupsEndpoint().get_group(group_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return result


@groups_routes.get("/api/groups", tags=["Groups"], operation_id="get_all_groups")
async def get_all_groups() -> List[dict]:
    return await GroupsEndpoint().get_all_groups()


@groups_routes.delete("/api/groups/{group_id}", tags=["Groups"], operation_id="delete_group")
async def delete_group(group_id: int) -> dict:
    success = await GroupsEndpoint().delete_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"status": "deleted"}