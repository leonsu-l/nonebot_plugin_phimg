from pydantic import BaseModel

class PersonalConfig(BaseModel):
    tags: list[str] = []

class PersonalId(BaseModel):
    __root__: dict[str, PersonalConfig] = {}