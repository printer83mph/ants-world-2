from baseconfig import BaseServiceSettings
from pydantic import Field


class SimulatorServiceSettings(BaseServiceSettings):
    """Settings specific to the simulator service"""

    fixed_dt: float = Field(description="Delta time between simulation timesteps")

    redis_url: str = Field(description="Connection URL for Redis")

    # JWT settings
    app_name: str = Field(
        default="antsworld2-simulator", description="Application name"
    )


settings = SimulatorServiceSettings()  # pyright: ignore[reportCallIssue]
