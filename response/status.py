from enum import Enum


class BaseStatusCode(Enum):
    """状态码基类"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    @classmethod
    def getByCode(cls, code: int, default=None):
        """通过 code 获取枚举成员"""
        for member in cls:
            if member.code == code:
                return member
        if default is None:
            raise ValueError(f"No matching member found with code {code}")
        return default


class CommonStatus(BaseStatusCode):

    """通用状态码"""
    SUCCESS = (200, "操作成功")
    BAD_REQUEST = (400, "请求参数错误")
    UNAUTHORIZED = (401, "未授权访问")
    FORBIDDEN = (403, "禁止访问")
    NOT_FOUND = (404, "资源不存在")
    INTERNAL_SERVER_ERROR = (500, "服务器内部错误")

    # 业务相关状态码 (可根据需要扩展)
    VALIDATE_ERROR = (422, "参数验证失败")
    RATE_LIMIT = (429, "请求过于频繁")

    def __init__(self, code: int, message: str):
        # 调用基类初始化
        super().__init__(code, message)
