"""
自定义异常类模块
"""
from typing import Any, Dict, Optional
from ..response.status import CommonStatus


class BaseAPIException(Exception):
    """API异常基类"""

    def __init__(
        self,
        code: CommonStatus = CommonStatus.INTERNAL_SERVER_ERROR,
        message: Optional[str] = None,
        data: Any = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message or code.message
        self.data = data
        self.extra_data = extra_data or {}
        super().__init__(self.message)


class BusinessException(BaseAPIException):
    """业务异常"""

    def __init__(
        self,
        message: str = "业务处理异常",
        data: Any = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=CommonStatus.BAD_REQUEST,
            message=message,
            data=data,
            extra_data=extra_data
        )


class ValidationException(BaseAPIException):
    """参数验证异常"""

    def __init__(
        self,
        message: str = "参数验证失败",
        data: Any = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=CommonStatus.VALIDATE_ERROR,
            message=message,
            data=data,
            extra_data=extra_data
        )


class AuthenticationException(BaseAPIException):
    """认证异常"""

    def __init__(
        self,
        message: str = "认证失败",
        data: Any = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=CommonStatus.UNAUTHORIZED,
            message=message,
            data=data,
            extra_data=extra_data
        )


class AuthorizationException(BaseAPIException):
    """授权异常"""

    def __init__(
        self,
        message: str = "权限不足",
        data: Any = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=CommonStatus.FORBIDDEN,
            message=message,
            data=data,
            extra_data=extra_data
        )


class NotFoundException(BaseAPIException):
    """资源不存在异常"""

    def __init__(
        self,
        message: str = "资源不存在",
        data: Any = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=CommonStatus.NOT_FOUND,
            message=message,
            data=data,
            extra_data=extra_data
        )


class RateLimitException(BaseAPIException):
    """频率限制异常"""

    def __init__(
        self,
        message: str = "请求过于频繁",
        data: Any = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=CommonStatus.RATE_LIMIT,
            message=message,
            data=data,
            extra_data=extra_data
        )
