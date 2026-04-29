from baseconfig import BaseServiceSettings
from pydantic import Field


class StreamServiceSetting(BaseServiceSettings):
    """Settings specific to the streaming service"""

    redis_url: str = Field(description="Connection URL for Redis")

    fixed_dt: float = Field(description="Delta time for simulation time-steps")
    fetch_interval: float = Field(description="How often to fetch sim data")

    app_name: str = Field(default="antsworld2-stream", description="Application name")


settings = StreamServiceSetting()  # pyright: ignore[reportCallIssue]
