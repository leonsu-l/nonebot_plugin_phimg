from functools import wraps

from nonebot.log import logger

from ...errors import NoImagesFoundError, DerpibooruAPIError
# from .cmd_handler import cmd

def handle_exceptions(func):
    """异常处理装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NoImagesFoundError as e:
            logger.error(f"无图片: {str(e)}")
            # await cmd.finish(f"无图片: {str(e)}")
        except DerpibooruAPIError as e:
            logger.error(f"Derpibooru API 错误: {str(e)}")
            # await cmd.finish(f"Derpibooru API 错误: {str(e)}")
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行异常: {str(e)}")
            raise
    return wrapper