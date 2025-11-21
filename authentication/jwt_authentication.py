from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from ..utils.crypto.jwt_ import JWTHandler
from ..utils.cache import DataCache
from ..utils.util import getUserModel

User = getUserModel()


class JWTAuthentication(BaseAuthentication):
    """
    JWT 认证
    """

    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token:
            raise exceptions.NotAuthenticated('未提供授权信息')

        login_data = DataCache.getData(token)

        if not login_data:
            raise exceptions.AuthenticationFailed("Token 不存在/已过期，请重新登录！")
        token_info = JWTHandler().decode(token)
        try:
            user = User.objects.get(id=token_info["user_id"])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("用户不存在！")
        except Exception as e:
            raise exceptions.AuthenticationFailed("用户不存在！")
        return user, token
