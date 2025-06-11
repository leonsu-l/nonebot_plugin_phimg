import argparse
from .argument_parser import CustomArgumentParser

parser = CustomArgumentParser(
    prog=".搜图",
    add_help=False,
    epilog=f"示例：\n  .搜图 <tags> # 直接通过标签搜索图片\n\n提示: \n  .和。均可作为命令前缀",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
    'tagss',
    nargs='?',
    action='store',
    type=str,
    metavar="<tags>",
    help='直接输入标签即可搜图（多个标签用逗号分隔）\n'
)
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
parser.add_argument(
    "--status",
    action="store_true",
    help="获取当前群聊的搜图功能状态"
)
