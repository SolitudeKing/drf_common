from datetime import datetime
from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.contrib.auth.models import (
    PermissionsMixin,
    UserManager
)
from django.contrib.auth.base_user import (
    AbstractBaseUser,
)
from django.core import validators
from django.utils.deconstruct import deconstructible
from .base_manager import BaseUserManager


class BaseModel(models.Model):
    """ 基础model """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="删除时间")

    class Meta:
        abstract = True  # 抽象模型类，用于继承，不会创建表

# 创建保存前的信号，当模型删除时自动设置删除时间，当模型恢复时自动取消删除时间


@receiver(pre_save, sender=BaseModel)
def preSaveHandler(sender, instance: BaseModel, **kwargs):
    # 检测is_deleted字段是否发生变化
    if instance.is_deleted != sender.objects.get(pk=instance.pk).is_deleted:
        if instance.is_deleted:
            instance.deleted_at = timezone.now()
        else:
            instance.deleted_at = None
            instance.created_at = timezone.now()
            instance.save()


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^[\w.@+-]+\Z"
    message = "请输入正确的用户名。要求. 30字以内。字母、数字和@/。/ + / - / _。"
    flags = 0


class AbstractUser(AbstractBaseUser, PermissionsMixin, BaseModel):

    username_validator = UsernameValidator()

    username = models.CharField(
        max_length=32,
        unique=True,
        null=True, blank=True,
        verbose_name="用户编号",
        help_text="要求! 30字以内,字母、数字和@/./ + / - / _号.",
    )
    password = models.CharField(max_length=128, verbose_name="密码")
    validators = [username_validator]
    email = models.EmailField(verbose_name="邮箱", null=True, blank=True)

    is_staff = models.BooleanField(
        verbose_name="staff status",
        default=False,
        help_text="用户是否可以登录到这个管理站点.",
    )
    is_active = models.BooleanField(
        verbose_name="是否激活",
        default=True,
        help_text=(
            "指定该用户是否应被视为活跃状态。 "
            "若要取消对账户的处理，请取消选中此选项，而非直接删除账户。"
        ),
    )

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]
    objects = UserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    class Meta:
        abstract = True
        verbose_name = "user"
        verbose_name_plural = "users"


class BaseUser(AbstractBaseUser, BaseModel):
    """ 基础用户模型 """

    username_validator = UsernameValidator()

    username = models.CharField(
        max_length=32,
        unique=True,
        null=True, blank=True,
        verbose_name="用户编号",
        help_text="要求! 30字以内,字母、数字和@/./ + / - / _号.",
    )

    password = models.CharField(max_length=128, null=True, blank=True, verbose_name="密码")
    validators = [username_validator]

    is_active = models.BooleanField(
        verbose_name="是否激活",
        default=True,
        help_text=(
            "指定该用户是否应被视为活跃状态。 "
            "若要取消对账户的处理，请取消选中此选项，而非直接删除账户。"
        ),
    )

    is_superuser = models.BooleanField(
        verbose_name="是否为管理员",
        default=False,
        help_text=(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = BaseUserManager()

    def __str__(self):
        return self.username

    class Meta:
        abstract = True
