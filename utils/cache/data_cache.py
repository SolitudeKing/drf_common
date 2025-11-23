from typing import Any, Optional

import logging
from django.conf import settings
from .redis import CommCache

logger = logging.getLogger(__name__)


class DataCache(CommCache):
    """
    数据缓存工具
    """

    @classmethod
    def getData(cls, cache_key: str) -> Optional[Any]:
        cache_data = cls.get(cache_key, pick_ser=True)
        return cache_data

    @classmethod
    def saveData(cls, token: str, data: Any, extra: Optional[dict] = None):
        extra = dict(extra or {})
        cache_data = {
            **extra,
            "data": data,
            "token": token,
        }
        timeout = getattr(settings, "LOGIN_EXPIRED_TIME", 60 * 60 * 24 * 7)
        cls.set(token, cache_data, timeout=timeout, pick_ser=True)

    @classmethod
    def updateData(cls, token: str, data: Any, extra: Optional[dict] = None):
        extra = dict(extra or {})
        cache_payload = cls.get(token, pick_ser=True)
        if not cache_payload:
            logger.debug("token %s 未命中缓存，跳过更新", token)
            return None

        timeout = cls.ttl(token)
        merged = dict(cache_payload)
        merged.update(extra)
        merged.update({"data": data, "token": token})
        if timeout and timeout > 0:
            cls.set(token, merged, timeout=timeout, pick_ser=True)
        else:
            cls.set(token, merged, pick_ser=True)
        return merged

    @classmethod
    def deleteData(cls, token: str) -> None:
        cls.delete(token)
