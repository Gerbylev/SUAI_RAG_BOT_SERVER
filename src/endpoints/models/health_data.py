from pydantic import BaseModel


class HealthData(BaseModel):
    """
    HealthData
    """  # noqa: E501

    status: str
