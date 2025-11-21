import datetime
from typing import Any, Optional, Dict, List
from .status import BaseStatusCode, CommonStatus
from django.http import JsonResponse
from django.core.paginator import Page, Paginator


class Response(JsonResponse):
    ...


class APIResponse:
    """统一API响应类"""

    def __init__(
            self,
            code: BaseStatusCode = CommonStatus.SUCCESS,
            msg: Optional[str] = None,
            data: Any = None,
            timestamp: Optional[str] = None,
            request_id: Optional[str] = None,
            **kwargs
    ):
        """
        初始化响应对象
        ===
        Args:
            code (BaseStatusCode): 状态码枚举
            msg (str): 状态信息
            data (Any): 响应数据
            timestamp (str): 时间戳
            request_id (str): 请求ID
            **kwargs: 其他参数
        """
        self.code = code
        self.msg = msg or code.message
        self.data = data
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.request_id = request_id
        self.extra = kwargs

        # self.data["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def result(self):
        """转换为字典格式"""
        result = {
            "code": self.code.code,
            "msg": self.msg,
            "results": self.data,
            "timestamp": self.timestamp,
        }
        # 添加请求ID（如果存在）
        if self.request_id:
            result["request_id"] = self.request_id

        # 添加额外参数
        if self.extra:
            result.update(self.extra)

        return result

    def toJsonResponse(self):
        """转换为JsonResponse"""
        # 设置HTTP状态码
        status = self.code.code

        # 创建响应
        response = Response(
            self.result,
            status=status,
            json_dumps_params={"ensure_ascii": False}
        )
        return response


class ResponseUtil:
    """响应工具类"""

    @staticmethod
    def success(data: Any = None, message: str = "操作成功", **kwargs) -> APIResponse:
        """成功响应"""
        return APIResponse(CommonStatus.SUCCESS, message, data, **kwargs)

    # @staticmethod
    # def created(data: Any = None, message: str = "创建成功", **kwargs) -> APIResponse:
    #     """创建成功响应"""
    #     return APIResponse(CommonStatus.CREATED, message, data, **kwargs)

    @staticmethod
    def error(
        code: CommonStatus = CommonStatus.INTERNAL_SERVER_ERROR,
        message: Optional[str] = None,
        data: Any = None,
        **kwargs
    ) -> APIResponse:
        """错误响应"""
        return APIResponse(code, message, data, **kwargs)

    @staticmethod
    def paginate(
        paginator: Paginator,
        page: int,
        data: List[Any],
        message: str = "获取成功"
    ) -> APIResponse:
        """分页响应"""
        return APIResponse(
            CommonStatus.SUCCESS,
            message,
            data,
            pagination={
                "total": paginator.count,
                "page": page,
                "page_size": paginator.per_page,
                "pages": paginator.num_pages,
                "has_prev": page > 1,
                "has_next": page < paginator.num_pages,
            }
        )

    # @staticmethod
    # def validateError(errors: Dict[str, Any], message: str = "参数验证失败") -> APIResponse:
    #     """参数验证错误响应"""
    #     return APIResponse(CommonStatus.VALIDATE_ERROR, message, errors)

    @staticmethod
    def notFound(message: str = "资源不存在") -> APIResponse:
        """资源不存在响应"""
        return APIResponse(CommonStatus.NOT_FOUND, message)

    @staticmethod
    def unauthorized(message: str = "未授权") -> APIResponse:
        """未授权响应"""
        return APIResponse(CommonStatus.UNAUTHORIZED, message)

    @staticmethod
    def forbidden(message: str = "禁止访问") -> APIResponse:
        """禁止访问响应"""
        return APIResponse(CommonStatus.FORBIDDEN, message)

# 快捷方法


def successResponse(data: Any = None, message: str = "操作成功", **kwargs) -> JsonResponse:
    """成功响应快捷方法"""
    return ResponseUtil.success(data, message, **kwargs).toJsonResponse()


def pageResponse(
    paginator: Paginator,
        page: int,
        data: List[Any],
        message: str = "获取成功") -> JsonResponse:
    """
    数据返回函数
    :return:
    """
    """分页响应快捷方法"""
    return ResponseUtil.paginate(paginator, page, data, message).toJsonResponse()


def errorResponse(
    code: CommonStatus = CommonStatus.INTERNAL_SERVER_ERROR,
        message: Optional[str] = None,
        data: Any = None,
        **kwargs) -> JsonResponse:
    """
    异常返回
    """
    """错误响应快捷方法"""
    return ResponseUtil.error(code, message, data, **kwargs).toJsonResponse()
