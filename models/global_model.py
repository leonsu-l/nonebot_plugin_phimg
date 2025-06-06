from pydantic import BaseModel

class GlobalConfig(BaseModel):
    key: str = ""
    enabled: bool = True
    tags: list[str] = ["safe"]
