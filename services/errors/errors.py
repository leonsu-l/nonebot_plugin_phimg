from typing import Optional

class PhilomenaAPIError(Exception):
    """Philomena API 基础异常类"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NoImagesFoundError(PhilomenaAPIError):
    """没有找到图片的异常"""
    def __init__(self, message: str = "未找到匹配的图片"):
        super().__init__(message)

class ImageNumberExceedError(PhilomenaAPIError):
    """图片数量超过限制的异常"""
    def __init__(self, requested: int, limit: int):
        message = f"获取到图片数量为 {requested} ，最多为 {limit} ，请适当减小范围后重试。"
        super().__init__(message)