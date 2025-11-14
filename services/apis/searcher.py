from random import randint
from urllib.parse import urlencode
from typing import Union
import aiohttp

from ..errors import PhilomenaAPIError, NoImagesFoundError

from nonebot.log import logger

ALLOWED_METHODS = ["images", "reverse"]
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

    @property
    def domain(self) -> str:
        return self._domain

    @domain.setter
    def domain(self, domain: str) -> None:
        """限定搜索域名"""
        if domain not in ALLOWED_DOMAINS:
            raise ValueError(f"Invalid domain. Must be one of: {', '.join(ALLOWED_DOMAINS)}")
        self._domain = domain
    
    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, method: str) -> None:
        """限定搜索方法"""
        if method not in ALLOWED_METHODS:
            raise ValueError("Invalid method. Must be one of: " + ", ".join(ALLOWED_METHODS))
        self._method = method
    
    @property
    def http_method(self) -> str:
        return self._http_method

    @http_method.setter
    def http_method(self, http_method: str) -> None:
        """设置 HTTP 请求方法"""
        if http_method.upper() not in ["GET", "POST"]:
            raise ValueError("Invalid HTTP method. Must be GET or POST")
        self._http_method = http_method.upper()

    async def _search(self) -> list[dict[str, Union[str, int]]]:
        """执行搜索请求"""
        api_url = f"https://{self.domain}/api/v1/json/search/{self.method}"
        logger.info(f"准备发送请求的参数: {self.params}")
        try:
            async with aiohttp.ClientSession() as session:
                if self._http_method == "GET":
                    query_str = urlencode(self.params, doseq=False, encoding='utf-8', safe='')
                    full_url = f"{api_url}?{query_str}"
                    logger.info(f"搜索API URL (GET): {full_url}")
                    async with session.get(full_url, headers=self.HEADERS) as response:
                        if response.status != 200:
                            raise PhilomenaAPIError(f"API 请求失败，状态码：{response.status}")
                        data = await response.json()
                else:  # POST
                    logger.info(f"搜索API URL (POST): {api_url}")
                    logger.debug(f"POST 数据: {self.params}")
                    async with session.post(api_url, data=self.params, headers=self.HEADERS) as response:
                        if response.status != 200:
                            raise PhilomenaAPIError(f"API 请求失败，状态码：{response.status}")
                        data = await response.json()
                
                if data["total"] == 0:
                    raise NoImagesFoundError()
                return data['images']
        except aiohttp.ClientError as e:
            raise PhilomenaAPIError(f"网络请求失败: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (PhilomenaAPIError, NoImagesFoundError)):
                raise
            raise PhilomenaAPIError(f"搜索过程出错: {str(e)}") from e


class Tags2ImgSearcher(Searcher):
    def __init__(self, params: dict):
        super().__init__(params)

    async def select_img(self, index: int = -1) -> dict[str, Union[str, int]]:
        """从搜索结果中选择一张图片"""
        images = await self._search()
        if index >= len(images) or index < 0:
            index = randint(0, len(images) - 1)
        return images[index]


class Img2ImgSearcher(Searcher):
    def __init__(self, params: dict):
        super().__init__(params)
        self.method = "reverse"
        self.http_method = "POST"  # 以图搜图使用 POST 方法

    async def select_img_list(self) -> list[dict[str, Union[str, int]]]:
        """获取相似图片列表"""
        images = await self._search()
        return images