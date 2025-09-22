from pydantic import BaseModel, Field
from nonebot import get_driver

class GlobalConfig(BaseModel):
    key: str = Field(default_factory=lambda: getattr(get_driver().config, "phimg_key", ""))
    enabled: bool = Field(default_factory=lambda: getattr(get_driver().config, "phimg_enabled", True))
    tags: list[str] = Field(default_factory=lambda: getattr(get_driver().config, "phimg_tags", ["safe"]))