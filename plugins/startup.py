from nonebot import get_driver
from nonebot.log import logger

driver = get_driver()

@driver.on_startup
async def _():
    pass