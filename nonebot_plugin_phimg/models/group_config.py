from pydantic import BaseModel, RootModel

class GroupConfig(BaseModel):
    enabled: bool = True
    onglobal: bool = True
    tags: list[str] = []

class GroupId(RootModel[dict[str, GroupConfig]]):
    pass