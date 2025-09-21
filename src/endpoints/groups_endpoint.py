from typing import List, Optional

from endpoints.models.test_data import TestRequest
from services.test_service import TestService


class GroupsEndpoint:
    def __init__(self):
        self.test_service = TestService()

    async def create_group(self, request: TestRequest) -> dict:
        return await self.test_service.create_group(request)

    async def get_group(self, group_id: int) -> Optional[dict]:
        return await self.test_service.get_group(group_id)

    async def get_all_groups(self) -> List[dict]:
        return await self.test_service.get_all_groups()

    async def delete_group(self, group_id: int) -> bool:
        return await self.test_service.delete_group(group_id)