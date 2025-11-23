import logging
from django.db import models
from ..utils.crypto.aes import AESHandler

AES_KEY = "ojbkmmpcode2025^"
encryptor = AESHandler(AES_KEY)

logger = logging.getLogger(__name__)


class EncryptedField(models.TextField):
    def from_db_value(self, value, expression, connection):
        """从数据库读取时解密"""
        try:
            return encryptor.decrypt(value)
        except Exception as e:
            logger.error(f"数据库=>模型: 解密失败：{str(e)}")
            return value

    def to_python(self, value):
        """转换为 Python 对象时解密"""
        if value is None:
            return value

        value = super().to_python(value)
        try:
            return encryptor.decrypt(value)
        except Exception as e:
            # 如果解密失败，说明 value 可能已经是明文，直接返回
            logger.error("Value=>Python: value已经是明文，无需转换")
            return value

    def get_prep_value(self, value):
        """保存到数据库前加密"""
        if value is None:
            return value
        value = super().get_prep_value(value)
        try:
            # 尝试解密，如果成功，说明它已经是加密过的，直接返回
            encryptor.decrypt(value)
            logger.error("模型=>数据库: value已经是加密过的，无需转换")
            return value
        except Exception:
            # 如果解密失败，说明是明文，进行加密

            return encryptor.encrypt(value)

    def validate(self, value, model_instance):
        return super().validate(value, model_instance)
