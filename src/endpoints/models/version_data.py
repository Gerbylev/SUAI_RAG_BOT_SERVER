from pydantic import BaseModel


class VersionData(BaseModel):
    component: str
    branch: str
    build_date: str
    changeset: str