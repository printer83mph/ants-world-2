from baseconfig import BaseServiceSettings
from pydantic import Field


class StreamServiceSetting(BaseServiceSettings):
    """Settings specific to the streaming service"""

    app_name: str = Field(default="antsworld2-stream", description="Application name")


settings = StreamServiceSetting()  # pyright: ignore[reportCallIssue]
