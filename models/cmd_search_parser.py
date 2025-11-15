import argparse
from .argument_parser import CustomArgumentParser

parser = CustomArgumentParser(
    prog=".搜图",
    add_help=False,
    epilog=f"示例：\n  .搜图 <tags> # 直接通过标签搜索图片\n\n提示: \n  .和。均可作为命令前缀\n  图搜图使用方式为引用图片，默认匹配距离为0.25\n",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
    'params',
    nargs='?',
    action='store',
    type=str,
    metavar="<tags|distance>",
    help='输入标签为tags搜图；输入匹配距离为图搜图\n'
)
parser.add_argument(
    '--help',
    action='help', 
    help='显示帮助信息'
)
parser.add_argument(
    "--tags",
    action="store_true",
    help="获取当前群聊内置标签列表"
)
parser.add_argument(
    "--status",
    action="store_true",
    help="获取当前群聊的搜图功能状态"
)