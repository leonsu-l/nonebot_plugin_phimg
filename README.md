### 使用方法
* 创建python环境（对应nonebot环境版本即可）
* 初始化nonebot2
  * __建议通过nonebot2官方脚手架初始化nonebot，一键安装环境依赖__
* 在你nonebot插件所在路径拉取仓库
* 通过```requirements.txt```安装所需pip包
* 源神，启动！

### 配置项
- ***PHIMG_KEY `str`***  
  &nbsp;&nbsp;&nbsp;&nbsp;API密钥  
- ***PHIMG_ENABLED `bool`***  
  &nbsp;&nbsp;&nbsp;&nbsp;是否默认启用插件
- ***PHIMG_TAGS `list[str]`***  
  &nbsp;&nbsp;&nbsp;&nbsp;全局标签
```python
# .env.prod
PHIMG_KEY="your_api_key"
PHIMG_ENABLED=True
PHIMG_TAGS=["safe"]
```

### 老插件
* [nonebot-plugin-dbimg](https://github.com/leonsu-l/nonebot-plugin-dbimg)
* 本插件是基于此插件功能的完全重构版
