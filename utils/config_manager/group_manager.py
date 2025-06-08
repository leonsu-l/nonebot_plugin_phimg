import json
from pathlib import Path
from functools import wraps

from ...models import GroupConfig, GroupId

def ensure_group_exists(func):
    """装饰器：确保 group_id 存在"""
    @wraps(func)
    def wrapper(self, group_id: str, *args, **kwargs):
        if group_id not in self.data.__root__:
            self.data.__root__[group_id] = GroupConfig()
        return func(self, group_id, *args, **kwargs)
    return wrapper

class GroupConfigManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self.load()

    def load(self) -> GroupId:
        """从 JSON 文件加载配置，如果文件不存在则返回一个空的 Data 对象"""
        if Path(self.file_path).exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            if "__root__" in loaded_data:
                return GroupId(__root__=loaded_data["__root__"])
            else:
                return GroupId(__root__=loaded_data)
        else:
            return GroupId()

    def save(self):
        """将当前的配置保存到 JSON 文件"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data.dict(), f, ensure_ascii=False, indent=2)

    def get_status(self, group_id: str) -> bool:
        """获取指定 group_id 的状态"""
        cfg = self.data.__root__.get(group_id)
        return cfg.enabled if cfg else True

    def get_tags(self, group_id: str) -> list[str]:
        """获取指定 group_id 的 tags"""
        cfg = self.data.__root__.get(group_id)
        return cfg.tags if cfg else []

    def get_all(self) -> dict[str, GroupConfig]:
        """返回所有 group_id 的配置"""
        return self.data.__root__

    @ensure_group_exists
    def update_tags(self, group_id: str, new_tags: list[str]):
        """更新指定 group_id 的 tags"""
        self.data.__root__[group_id].tags = new_tags
        self.save()

    @ensure_group_exists
    def add_tags(self, group_id: str, tags: list[str]):
        """向指定 group_id 的 tags 中添加一列 tags"""
        for tag in tags:
            if tag not in self.data.__root__[group_id].tags:
                self.data.__root__[group_id].tags.append(tag)
        self.save()

    @ensure_group_exists
    def remove_tags(self, group_id: str, tags: list[str]):
        """从指定 group_id 的 tags 中删除一列 tags"""
        for tag in tags:
            if tag in self.data.__root__[group_id].tags:
                self.data.__root__[group_id].tags.remove(tag)
        self.save()

    @ensure_group_exists
    def enable(self, group_id: str):
        """启用指定 group_id 的配置"""
        self.data.__root__[group_id].enabled = True
        self.save()

    @ensure_group_exists
    def disable(self, group_id: str):
        """禁用指定 group_id 的配置"""
        self.data.__root__[group_id].enabled = False
        self.save()