import argparse
from io import StringIO

class CustomArgumentParser(argparse.ArgumentParser):
    """自定义ArgumentParser，将错误和帮助信息写入字符串而不是stderr/stdout"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('prefix_chars', '--')
        super().__init__(*args, **kwargs)
        self.output_buffer = StringIO()
        self.has_error = False
        # 自定义错误消息映射
        self.custom_error_messages = {
            'unrecognized arguments': '未识别的参数',
            'invalid choice': '无效的选择',
            'argument is required': '缺少必需的参数',
            'expected one argument': '需要一个参数',
            'expected at least one argument': '至少需要一个参数',
        }
        self.custom_help_text = {
            'usage': '用法',
            'positional arguments': '主要参数',
            'options': '附加参数',
        }
        
    def _parse_optional(self, arg_string):
        """重写可选参数解析，只处理双横线参数"""
        # 只有以双横线开头的才被视为选项参数
        if arg_string.startswith('--'):
            return super()._parse_optional(arg_string)
        else:
            # 单横线开头的视为位置参数
            return None

    def _customize_error_message(self, message):
        """自定义错误消息"""
        error_parts = message.split(':', 1)
        appended_message = error_parts[1].strip() if len(error_parts) > 1 else ''
        
        for key, custom_msg in self.custom_error_messages.items():
            if key in message.lower():
                return f"{custom_msg}: {appended_message}"
        
        # 如果没有匹配的自定义错误消息，返回原始消息
        return message
            
    def _customize_help_text(self, help_text):
        """自定义帮助文本"""
        for key, custom_msg in self.custom_help_text.items():
            if key in help_text.lower():
                help_text = help_text.replace(key, custom_msg)
        return help_text

    def error(self, message):
        """重写error方法，将错误信息写入缓冲区而不是退出程序"""
        self.has_error = True
        custom_message = self._customize_error_message(message)
        self.output_buffer = StringIO()
        self.output_buffer.write(f"错误: {custom_message}")
        raise SystemExit()
    
    def print_help(self, file=None):
        """重写print_help方法，将帮助信息写入缓冲区"""
        help_text = self.format_help()
        custom_help_text = self._customize_help_text(help_text)
        self.clear_output()
        self.output_buffer.write(custom_help_text)
    
    def get_output(self) -> str:
        """获取输出内容"""
        return self.output_buffer.getvalue()
    
    def clear_output(self) -> None:
        """清空输出缓冲区"""
        self.output_buffer = StringIO()
        self.has_error = False

'''
# 示例：使用自定义parser
cmd_parser = CustomArgumentParser(
    description="搜图命令",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
'''