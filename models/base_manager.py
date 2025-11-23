from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.base_user import (
    BaseUserManager as DJ_BaseUserManager,
)


class BaseUserManager(DJ_BaseUserManager):
    def _create_user(self, username, password, **extra_fields):
        """
        使用给定的用户名和密码创建一个新用户.
        """
        if not username:
            raise ValueError("The given username must be set")

        user = self.model(username=username ** extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):

        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):

        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, **extra_fields)
