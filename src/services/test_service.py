from typing import List, Optional

from dao.group import Group
from db.transaction import transactional
from endpoints.models.test_data import TestRequest


class TestService:
    @transactional
    async def create_group(self, request: TestRequest) -> dict:
        group = await Group.create(request.name)
        return {"id": group.id, "name": group.name, "status": "created"}

    @transactional
    async def get_group(self, group_id: int) -> Optional[dict]:
        group = await Group.get_by_id(group_id)
        if group:
            return {"id": group.id, "name": group.name}
        return None

    @transactional
    async def get_all_groups(self) -> List[dict]:
        groups = await Group.get_all()
        return [{"id": group.id, "name": group.name} for group in groups]

    @transactional
    async def delete_group(self, group_id: int) -> bool:
        return await Group.delete_by_id(group_id)