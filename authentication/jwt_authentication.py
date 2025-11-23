from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework.authentication import BaseAuthentication
from ..utils.crypto.jwt_ import JWTHandler

# User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    JWT 认证
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request: Request):
        token = self.getToken(request)
        if not token:
            raise exceptions.NotAuthenticated("未提供授权信息")
        validated_token = self.getValidatedToken(token)
        return self.getUser(validated_token), token

    def getToken(self, request: Request) -> str:
        """
        获取令牌
        """
        token = request.headers.get("Authorization")
        if isinstance(token, bytes):
            token = token.decode()

        return token.strip()

    def getValidatedToken(self, token: str) -> str:
        try:
            validated_token = JWTHandler().decode(token, verify_exp=True)
        except Exception as e:
            raise exceptions.AuthenticationFailed("令牌已过期！") from e

        return validated_token

    def getUser(self, validated_token: str):
        """
        尝试使用已验证的令牌查找并找回用户。
        """

        try:
            user = self.user_model.objects.get(id=validated_token["user_id"])
        except self.user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed("用户不存在！") from e
        except Exception as e:
            raise exceptions.AuthenticationFailed("用户不存在！") from e
        return user
