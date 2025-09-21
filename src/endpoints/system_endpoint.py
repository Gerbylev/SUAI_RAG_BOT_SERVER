import json
import os

from pydantic import BaseModel

__VERSION_FILE__ = "version-info.json"


class HealthData(BaseModel):
    """
    HealthData
    """  # noqa: E501

    status: str


class VersionData(BaseModel):
    component: str
    branch: str
    build_date: str
    changeset: str


class SystemEndpoint:
    def __init__(self):
        self.version_info = self.__load_version_info()

    @staticmethod
    def __load_version_info() -> VersionData:
        if os.path.isfile(__VERSION_FILE__):
            with open(__VERSION_FILE__) as f:
                return VersionData(**json.loads(f.read()))
        else:
            return VersionData(component="rag-server", branch="", build_date="", changeset="")

    def health(self) -> HealthData:
        return HealthData(status="Ok")

    def version(self) -> VersionData:
        return self.version_info

    def spec_yml(self) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        spec_path = os.path.join(os.path.dirname(current_dir), "spec.yml")

        with open(spec_path, "r") as file:
            spec_content = file.read()

        return spec_content
