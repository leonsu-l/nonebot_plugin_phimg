import argparse

parser = argparse.ArgumentParser(prog="搜图", add_help=False)
parser.add_argument(
    '--help',
    action='help', 
    help='显示帮助信息'
)
parser.add_argument(
    "--add",
    action="store",
    type=str,
    metavar="<tags>",
    help="添加标签，多个标签用逗号分隔"
)
parser.add_argument(
    "--rm",
    action="store",
    type=str,
    metavar="<tags>",
    help="删除标签，多个标签用逗号分隔"
)
parser.add_argument(
    "--tags",
    action="store_true",
    help="获取当前群聊内置标签列表"
)
parser.add_argument(
    "--on",
    action="store_true",
    help="开启当前群聊的搜图功能"
)
parser.add_argument(
    "--off",
    action="store_true",
    help="关闭当前群聊的搜图功能"
)
