from pydantic import BaseModel

class GlobalConfig(BaseModel):
    key: str
    enabled: bool
    tags: list[str]
