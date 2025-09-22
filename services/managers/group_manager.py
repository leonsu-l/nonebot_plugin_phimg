import json
import aiofiles
from pathlib import Path
from functools import wraps

from ...models import GroupConfig, GroupId

def _ensure_group_exists(func):
    """装饰器：确保 group_id 及其配置存在"""
    @wraps(func)
    def wrapper(self, group_id: str, *args, **kwargs):
        if group_id not in self.data.__root__:
            self.data.__root__[group_id] = GroupConfig()
        return func(self, group_id, *args, **kwargs)
    return wrapper

class GroupConfigManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None

    async def init(self):
        """异步初始化，加载配置"""
        self.data = await self.load()

    async def load(self) -> GroupId:
        """从 JSON 文件异步加载配置"""
        if Path(self.file_path).exists():
            async with aiofiles.open(self.file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                loaded_data = json.loads(content)
            return GroupId.parse_obj(loaded_data)
        else:
            return GroupId()

    async def save(self):
        """将当前的配置保存到 JSON 文件"""
        data_dict = self.data.dict()
        # 如果字典中有 "__root__" 键，直接使用其值
        if "__root__" in data_dict and len(data_dict) == 1:
            final_data = data_dict["__root__"]
        else:
            final_data = data_dict
        async with aiofiles.open(self.file_path, "w", encoding="utf-8") as f:
            content = json.dumps(final_data, ensure_ascii=False, indent=2)
            await f.write(content)

    def get_status(self, group_id: str) -> bool:
        """获取指定 group_id 的状态"""
        cfg = self.data.__root__.get(group_id)
        return cfg.enabled if cfg else True

    def get_tags(self, group_id: str) -> list[str]:
        """获取指定 group_id 的 tags"""
        cfg = self.data.__root__.get(group_id)
        return cfg.tags if cfg else []
    
    def get_onglobal(self, group_id: str) -> bool:
        """获取指定 group_id 的 onglobal 状态"""
        cfg = self.data.__root__.get(group_id)
        return cfg.onglobal if cfg else True

    @_ensure_group_exists
    def get_info(self, group_id: str) -> GroupConfig:
        """返回当前 group_id 的配置"""
        cfg = self.data.__root__.get(group_id)
        if not cfg:
            raise ValueError()
        return cfg

    @_ensure_group_exists
    async def update_tags(self, group_id: str, new_tags: list[str]):
        """更新指定 group_id 的 tags"""
        self.data.__root__[group_id].tags = new_tags
        await self.save()

    @_ensure_group_exists
    async def add_tags(self, group_id: str, added_tags: list[str]):
        """向指定 group_id 的 tags 中添加一列 tags"""
        current_tags = self.get_tags(group_id)
        all_tags = current_tags + list(added_tags)
        self.data.__root__[group_id].tags = list(set(all_tags))
        await self.save()

    @_ensure_group_exists
    async def remove_tags(self, group_id: str, tags: list[str]):
        """从指定 group_id 的 tags 中删除一列 tags"""
        for tag in tags:
            if tag in self.data.__root__[group_id].tags:
                self.data.__root__[group_id].tags.remove(tag)
        await self.save()

    @_ensure_group_exists
    async def enable(self, group_id: str):
        """启用指定 group_id 的配置"""
        self.data.__root__[group_id].enabled = True
        await self.save()

    @_ensure_group_exists
    async def disable(self, group_id: str):
        """禁用指定 group_id 的配置"""
        self.data.__root__[group_id].enabled = False
        await self.save()

    @_ensure_group_exists
    async def set_onglobal(self, group_id: str):
        """设置指定 group_id 的 onglobal 状态"""
        self.data.__root__[group_id].onglobal = True
        await self.save()

    @_ensure_group_exists
    async def set_offglobal(self, group_id: str):
        """设置指定 group_id 的 onglobal 状态"""
        self.data.__root__[group_id].onglobal = False
        await self.save()