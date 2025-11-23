import datetime
import logging
from typing import Any, Mapping, Optional

import jwt

logger = logging.getLogger(__name__)

# 默认配置常量
DEFAULT_JWT_KEY = "*9f0-b88xb%b=z$+md7h^1ey4-!fr!9eaj_cfg65g3g1l%$0o"
DEFAULT_ALGORITHM = "HS256"
DEFAULT_EXPIRES_IN = 60 * 60 * 24 * 7  # 7天（秒）
DEFAULT_ISSUER = "jwt_handler"
DEFAULT_LEEWAY = 5  # 时间验证宽容度（秒）


class JWTDecodeError(Exception):
    """当JWT解码或验证失败时抛出"""


class JWTHandler:
    """
    轻量级JWT工具类，基于PyJWT封装，提供一致的默认配置和错误处理
    实例化时可自定义密钥、算法、过期时间等参数
    """

    def __init__(
        self,
        secret: str = DEFAULT_JWT_KEY,
        algorithm: str = DEFAULT_ALGORITHM,
        expires_in: int = DEFAULT_EXPIRES_IN,
        issuer: str = DEFAULT_ISSUER,
        leeway: int = DEFAULT_LEEWAY
    ):
        """
        初始化JWT工具类

        Args:
            secret: 加密密钥（默认使用全局默认密钥）
            algorithm: 加密算法（默认HS256）
            expires_in: 默认过期时间（秒，默认7天）
            issuer: 签发者标识（默认"jwt_handler"）
            leeway: 时间验证宽容度（秒，默认5秒，处理服务器时间偏差）
        """
        self.secret = secret
        self.algorithm = algorithm
        self.expires_in = expires_in
        self.issuer = issuer
        self.leeway = leeway

    def _buildPayload(self, payload: Mapping[str, Any], expires_in: Optional[int]) -> dict:
        """
        构建JWT载荷（添加标准字段）

        Args:
            payload: 自定义载荷数据
            expires_in: 覆盖默认过期时间（秒）；传0表示永不过期
        Returns:
            完整的JWT载荷字典
        """
        result = dict(payload)
        # 签发时间（带UTC时区的时间）
        issued_at = datetime.datetime.now(datetime.UTC)
        # 设置签发者（默认使用实例配置的issuer）
        result.setdefault("iss", self.issuer)
        # 设置签发时间
        result.setdefault("iat", issued_at)
        # 计算过期时间
        ttl = expires_in if expires_in is not None else self.expires_in
        if ttl and ttl > 0:
            result["exp"] = issued_at + datetime.timedelta(seconds=ttl)
        return result

    def encode(self, payload: Mapping[str, Any], expires_in: Optional[int] = None) -> str:
        """
        将载荷编码为JWT字符串

        Args:
            payload: 可JSON序列化的任意数据（如字典）
            expires_in: 可选，覆盖默认过期时间（秒）；传0表示永不过期
        Returns:
            编码后的JWT字符串
        """
        full_payload = self._buildPayload(payload, expires_in)
        token = jwt.encode(full_payload, self.secret, algorithm=self.algorithm)
        # 兼容旧版PyJWT（可能返回bytes类型）
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    def decode(self, token: str, verify_exp: bool = True) -> dict:
        """
        解码JWT字符串并验证有效性

        Args:
            token: JWT字符串
            verify_exp: 是否验证过期时间（默认验证）
        Returns:
            解码后的载荷字典
        Raises:
            JWTDecodeError: 解码失败或验证不通过时抛出
        """
        try:
            decoded = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={
                    "verify_exp": verify_exp,
                    "require": ["iat"]
                },
                leeway=self.leeway
            )
        except jwt.ExpiredSignatureError as exc:
            logger.debug("JWT已过期: %s", exc)
            raise JWTDecodeError("令牌已过期") from exc
        except jwt.PyJWTError as exc:
            logger.debug("JWT解码失败: %s", exc)
            raise JWTDecodeError("无效的令牌") from exc
        return decoded


if __name__ == "__main__":
    # 1. 使用默认配置实例化
    default_handler = JWTHandler()
    payload = {"user_id": 100, "role": "admin"}
    token = default_handler.encode(payload)
    print("默认配置生成的token:", token)
    print("默认配置解码结果:", default_handler.decode(token), "\n")

    # 2. 自定义参数实例化（例如：修改密钥、过期时间为10分钟）
    custom_handler = JWTHandler(
        secret="my_custom_secret_123",
        expires_in=600,  # 10分钟
        issuer="my_app"
    )
    custom_token = custom_handler.encode(payload)
    print("自定义配置生成的token:", custom_token)
    print("自定义配置解码结果:", custom_handler.decode(custom_token))

    # 3. 测试错误场景（用错误的密钥解码）
    try:
        default_handler.decode(custom_token)  # 用默认密钥解码自定义token（会失败）
    except JWTDecodeError as e:
        print("预期错误:", e)
