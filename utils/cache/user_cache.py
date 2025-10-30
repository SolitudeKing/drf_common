from django.conf import settings
import pickle
from .redis import CommCache
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..util import getUserModel
User = getUserModel()


class UserCache(CommCache):

    @classmethod
    def getLoginUser(cls, cache_key: str):
        login_data = cls.get(cache_key, pick_ser=True)
        return login_data

    @classmethod
    def saveLoginUesr(cls, token, user, extra: dict = {}):
        login_data = {
            **extra,
            "user": user,
            "token": token,
        }
        if hasattr(settings, "LOGIN_EXPIRED_TIME"):
            timeout = settings.LOGIN_EXPIRED_TIME
        else:
            timeout = 60 * 60 * 24 * 7
        cls.set(token, login_data, timeout=timeout, pick_ser=True)

    @classmethod
    def updateLoginUser(cls, token, user, extra: dict = {}):
        try:

            us = cls.get(token, pick_ser=True)
            if us:
                cls.delete(token)
                data: dict = us
                data.update(extra)
                data.update({"user": user, "token": token})
                cls.set(
                    cache_key=token,
                    data=data,
                    timeout=cls.ttl(token),
                    pick_ser=True
                )
        except:  # 未登录情况
            pass

    def delLoginUser(self):
        self.delete()


@receiver(post_save, sender=User)
def clear_user_cache(sender, instance, **kwargs):
    # 清除与该用户相关的缓存
    if hasattr(instance, "login_token"):
        if hasattr(instance, "login_token"):
            UserCache(instance.login_token).delLoginUser()
