import aiohttp
from urllib.parse import urlencode
from typing import Union

from ....errors import DerpibooruAPIError, NoImagesFoundError

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

async def _(
    q: list[str],
    per_page: int = 50,
    key: str = "",
    page: int = 1,
    sf: str = "score",
    sd: str = "desc",
    timeout: int = 30
) -> list[dict[str, Union[str, int, float]]]:
    """
    通过标签搜索图片
    
    Args:
        q: 搜索标签列表（必需）
        per_page: 每页图片数量
        key: Derpibooru API 密钥
        page: 页码
        sf: 排序字段 (score, created_at, etc.)
        sd: 排序方向 (desc, asc)
        timeout: 请求超时时间（秒）
        
    Returns:
        图片数据列表
        
    Raises:
        NoImagesFoundError: 未找到匹配的图片
        DerpibooruAPIError: API 请求失败
    """
    if not q:
        raise ValueError("api内部错误: 搜索标签不能为空")
    
    # 构建查询参数
    query_params = {
        "key": key,
        "page": page,
        "per_page": per_page,
        "q": ",".join(q),
        "sf": sf,
        "sd": sd
    }
    
    # 移除空值参数
    query_params = {k: v for k, v in query_params.items() if v}
    
    query_str = urlencode(query_params, doseq=False, encoding='utf-8', safe='')
    api_url = f"https://derpibooru.org/api/v1/json/search/images?{query_str}"
    
    try:
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_config, headers=headers) as session:
            async with session.get(api_url) as response:
                response.raise_for_status()  # 检查 HTTP 状态码
                data = await response.json()

                if data.get('total') == 0:
                    raise NoImagesFoundError()
                    
                return data.get('images', [])
                
    except aiohttp.ClientError as e:
        raise DerpibooruAPIError(f"API 请求失败: {e.args[0]}: {e.args[1].message}")
    except NoImagesFoundError:
        raise
    except Exception as e:
        raise DerpibooruAPIError(f"处理响应时出错: {e}")