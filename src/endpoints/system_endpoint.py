import json
import os

from endpoints.models.health_data import HealthData
from endpoints.models.version_data import VersionData

__VERSION_FILE__ = "version-info.json"


version_info = VersionData(component="rag-server", branch="", build_date="", changeset="")
if os.path.isfile(__VERSION_FILE__):
    with open(__VERSION_FILE__) as f:
        version_info = VersionData(**json.loads(f.read()))

def health_endpoint() -> HealthData:
    return HealthData(status="Ok")

def version_endpoint() -> VersionData:
    return version_info

