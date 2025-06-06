import asyncio
from urllib.parse import urlencode

import aiohttp

async def _():
    query = {
        'key': "",
        'page': 1,
        'per_page': 50,
        'q': ["safe", "pony@%#@%$"],
        'sf': 'score',
        'sd': 'desc'
    }
    query['q'] = ",".join(query['q'])
    str_query = urlencode(query, doseq=False, encoding='utf-8', safe='')
    API_URL = f"https://derpibooru.org/api/v1/json/search/images?{str_query}"
    print(API_URL)

    async with aiohttp.ClientSession() as session:
        # try:
            async with session.get(API_URL) as resp:
                data = await resp.json()
                if data['total'] == 0:
                     print("没有找到相关图片")
                print(data['images'][0]["representations"]["large"])
        # except Exception as e:
        #     print(f"搜索图片时发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(_())