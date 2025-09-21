### 使用方法
* 创建python环境（没有版本要求）
* 初始化nonebot2
  * __建议通过nonebot2官方脚手架初始化nonebot，一键安装环境依赖__
* 在你nonebot插件所在路径拉取仓库
* 通过```requirements.txt```安装所需pip包
* 源神，启动！

### 配置项
- ***DBIMG_KEY `str`***  
  &nbsp;&nbsp;&nbsp;&nbsp;API密钥  
- ***DBIMG_ENABLED `bool`***  
  &nbsp;&nbsp;&nbsp;&nbsp;是否默认启用插件
- ***DBIMG_TAGS `list[str]`***  
  &nbsp;&nbsp;&nbsp;&nbsp;全局标签
```python
# .env.prod
DBIMG_KEY="your_api_key"
DBIMG_ENABLED=True
DBIMG_TAGS=["safe"]
```

### 老插件
* [nonebot-plugin-dbimg](https://github.com/leonsu-l/nonebot-plugin-dbimg)
* 本插件是基于此插件功能的完全重构版
