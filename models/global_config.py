from pydantic import BaseModel, Field
from nonebot import get_driver

class GlobalConfig(BaseModel):
    key: str = Field(default_factory=lambda: getattr(get_driver().config, "dbimg_key", ""))
    enabled: bool = Field(default_factory=lambda: getattr(get_driver().config, "dbimg_enabled", True))
    tags: list[str] = Field(default_factory=lambda: getattr(get_driver().config, "dbimg_tags", ["safe"]))
