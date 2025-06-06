from pydantic import BaseModel

class GroupConfig(BaseModel):
    enabled: bool = True
    tags: list[str] = []

class GroupId(BaseModel):
    __root__: dict[str, GroupConfig]