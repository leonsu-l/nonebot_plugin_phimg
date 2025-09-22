from pathlib import Path
import os

from .global_manager import GlobalConfigManager
from .group_manager import GroupConfigManager

CONFIG_PATH = (Path(__file__).parent.parent.parent / "config").resolve()

if not CONFIG_PATH.exists():
    os.makedirs(CONFIG_PATH, exist_ok=True)

__global_config_json = str(CONFIG_PATH / "global_config.json")
global_cfg = GlobalConfigManager(__global_config_json)

__group_config_json = str(CONFIG_PATH / "group_config.json")
group_cfg = GroupConfigManager(__group_config_json)

async def init():
    """初始化配置管理器"""
    await global_cfg.init()
    await group_cfg.init()