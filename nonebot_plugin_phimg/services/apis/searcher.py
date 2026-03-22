from random import randint
from urllib.parse import urlencode
from typing import Union, Any
import aiohttp
from aiohttp import ClientTimeout

from ..errors import *

from nonebot.log import logger

ALLOWED_METHODS = ["images", "reverse"]
ALLOWED_HTTP_METHODS = ["GET", "POST"]
ALLOWED_DOMAINS = [
    "derpibooru.org", 
    "trixiebooru.org", 
    "tantabus.ai",
    "ponybooru.org"
]

class Searcher:
    
    HEADERS = {"Accept": "application/json"}
    REQUEST_TIMEOUT = 30  # 秒

    def __init__(self, params: dict):
        self.params = params
        self._domain = "derpibooru.org"
        self._method = "images"
        self._http_method = "GET"  # HTTP 请求方法: GET 或 POST
        self._timeout = ClientTimeout(total=self.REQUEST_TIMEOUT)

    @property
    def domain(self) -> str:
        """获取当前搜索域名"""
        return self._domain

    @domain.setter
    def domain(self, domain: str) -> None:
        """设置搜索域名"""
        if domain not in ALLOWED_DOMAINS:
            raise ValueError(f"无效的域名。必须是以下之一: {', '.join(ALLOWED_DOMAINS)}")
        self._domain = domain
    
    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, method: str) -> None:
        """限定搜索方法"""
        if method not in ALLOWED_METHODS:
            raise ValueError("无效的方法。必须是以下之一: " + ", ".join(ALLOWED_METHODS))
        self._method = method
    
    @property
    def http_method(self) -> str:
        return self._http_method

    @http_method.setter
    def http_method(self, http_method: str) -> None:
        """设置 HTTP 请求方法"""
        if http_method.upper() not in ALLOWED_HTTP_METHODS:
            raise ValueError("无效的 HTTP 方法。必须是 GET 或 POST")
        self._http_method = http_method.upper()

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> dict[str, Any]:
        """发送 HTTP 请求"""
        try:
            if self.http_method == "GET":
                query_str = urlencode(self.params, doseq=False, encoding='utf-8', safe='')
                full_url = f"{url}?{query_str}"
                logger.info(f"搜索API URL (GET): {full_url}")
                
                async with session.get(
                    full_url, 
                    headers=self.HEADERS,
                    timeout=self._timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
            else:  # POST
                logger.info(f"搜索API URL (POST): {url}")
                logger.debug(f"POST 参数: {self.params}")
                
                async with session.post(
                    url, 
                    data=self.params, 
                    headers=self.HEADERS,
                    timeout=self._timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientResponseError as e:
            raise PhilomenaAPIError(f"API 请求失败，状态码：{e.status}，消息：{e.message}") from e
        except aiohttp.ClientError as e:
            raise PhilomenaAPIError(f"网络请求失败: {str(e)}") from e

    async def _search(self) -> list[dict[str, Union[str, int]]]:
        """执行搜索请求"""
        api_url = f"https://{self.domain}/api/v1/json/search/{self.method}"
        logger.info(f"准备发送请求的参数: {self.params}")
        
        try:
            async with aiohttp.ClientSession() as session:
                data = await self._make_request(session, api_url)
                total = data.get("total", 0)
                
                if total == 0:
                    logger.warning("搜索未返回任何图片")
                    raise NoImagesFoundError()
                
                if total > 10:
                    logger.info(f"搜索返回总计 {total} 张图片")
                    raise ImageNumberExceedError(total, 10)
                    
                images = data.get('images', [])
                logger.info(f"搜索成功，找到 {total} 张图片")
                return images
                
        except PhilomenaAPIError:
            raise
        except Exception as e:
            logger.exception(f"搜索过程出现未预期的错误: {str(e)}")
            raise PhilomenaAPIError(f"搜索过程出错: {str(e)}") from e


class Tags2ImgSearcher(Searcher):
    """标签搜图"""

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        self.method = "images"
        self.http_method = "GET"

    async def select_img(self, index: int = -1) -> dict[str, Union[str, int]]:
        """从搜索结果中选择一张图片"""
        images = await self._search()
        if not images:
            raise NoImagesFoundError()
            
        if index < 0 or index >= len(images):
            index = randint(0, len(images) - 1)
            logger.debug(f"随机选择第 {index} 张图片")
        else:
            logger.debug(f"选择第 {index} 张图片")
        return images[index]


class Img2ImgSearcher(Searcher):
    """图搜图"""

    def __init__(self, params: dict):
        super().__init__(params)
        self.method = "reverse"
        self.http_method = "POST"  # 以图搜图使用 POST 方法

    async def select_img_list(self) -> list[dict[str, Union[str, int]]]:
        """获取相似图片列表"""
        images = await self._search()
        return images