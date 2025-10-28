from django.conf import settings
from django.contrib.auth import get_user_model
from .redis import CommCache
from django.db.models.signals import post_save
from django.dispatch import receiver
import pickle
User = get_user_model()


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
                _extra: dict = us
                _extra.update(extra)
                _extra.update({"user": user, "token": token})
                cls.set(
                    _extra,
                    timeout=cls.ttl(token),
                    new_key=token,
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
