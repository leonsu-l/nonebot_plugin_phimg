from pathlib import Path

from .global_manager import GlobalConfigManager
from .group_manager import GroupConfigManager

CONFIG_PATH = Path(__file__).parent.parent.parent / "config"

__global_config_json = str(CONFIG_PATH / "global_config.json")
global_cfg = GlobalConfigManager(__global_config_json)

__group_config_json = str(CONFIG_PATH / "group_config.json")
group_cfg = GroupConfigManager(__group_config_json)
