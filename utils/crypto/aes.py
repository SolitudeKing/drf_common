import base64
import hashlib
import os
from typing import Union, Optional  # 导入类型工具
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from threading import Thread


class AESHandler:
    """
    AES加解密工具类（基于CBC模式，支持PKCS7填充）

    支持功能：
    - 字符串/字节数据的加解密
    - 自动生成符合长度的随机密钥
    - 自动管理IV向量（加密时生成，解密时提取）
    - 异常处理与详细错误提示
    """
    # AES块大小固定为16字节
    BLOCK_SIZE: int = AES.block_size

    def __init__(self, key: Optional[str] = None):
        """
        初始化AES工具

        :param key: 加密密钥（字符串），若为None则使用默认密钥
                    要求：utf-8编码后长度必须为16/24/32字节（对应128/192/256位）
        """
        # 默认密钥（确保utf-8编码后为16字节）
        defaultKey: str = "okmnhytfcde2025^"
        self.key: bytes = key.encode("utf-8") if key else defaultKey.encode("utf-8")
        self._validateKey()

    def _validateKey(self) -> None:
        """验证密钥长度是否符合AES要求"""
        keyLen: int = len(self.key)
        if keyLen not in (16, 24, 32):
            raise ValueError(f"密钥长度必须为16/24/32字节（当前{keyLen}字节）")

    @staticmethod
    def generateRandomKey(bitLength: int = 128) -> str:
        """
        生成随机AES密钥

        :param bitLength: 密钥位数（128/192/256）
        :return: 随机密钥字符串（utf-8编码安全）
        """
        if bitLength not in (128, 192, 256):
            raise ValueError("密钥位数必须为128/192/256")
        byteLength: int = bitLength // 8
        # 生成随机字节并转换为可打印字符串（base64确保安全编码）
        randomBytes: bytes = os.urandom(byteLength)
        return base64.urlsafe_b64encode(randomBytes).decode("utf-8").strip('=')

    def md5Hash(self, inputStr: str) -> str:
        """
        计算字符串的MD5哈希（大写）

        :param inputStr: 输入字符串
        :return: MD5哈希值（32位大写）
        """
        md5 = hashlib.md5()
        md5.update(inputStr.encode("utf-8"))
        return md5.hexdigest().upper()

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        AES加密（CBC模式+PKCS7填充+Base64编码）

        :param data: 待加密数据（字符串或字节）
        :return: 加密后的Base64字符串（格式：IV+密文 拼接后编码）
        """
        try:
            # 处理输入数据（转为字节）
            if isinstance(data, str):
                dataBytes: bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                dataBytes: bytes = data
            else:
                raise TypeError("输入数据必须是字符串或字节")

            # 生成随机IV（CBC模式必须，长度=块大小16字节）
            iv: bytes = os.urandom(self.BLOCK_SIZE)

            # 初始化加密器
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

            # 填充数据并加密
            paddedData: bytes = pad(dataBytes, self.BLOCK_SIZE, style="pkcs7")
            encryptedBytes: bytes = cipher.encrypt(paddedData)

            # 拼接IV和密文（IV用于解密，需一起传输）
            combined: bytes = iv + encryptedBytes

            # Base64编码为字符串（移除换行符）
            return base64.b64encode(combined).decode("utf-8").replace("\n", "")

        except Exception as e:
            raise RuntimeError(f"加密失败：{str(e)}")

    def decrypt(self, encryptedStr: Union[str, bytes]) -> str:
        """
        AES解密（Base64解码+CBC模式+PKCS7去填充）

        :param encryptedStr: 加密后的Base64字符串或字节
        :return: 解密后的原始字符串
        """
        try:
            # 处理输入数据（转为字节）
            if isinstance(encryptedStr, str):
                encryptedBytes: bytes = encryptedStr.encode("utf-8")
            elif isinstance(encryptedStr, bytes):
                encryptedBytes: bytes = encryptedStr
            else:
                raise TypeError("输入数据必须是字符串或字节")

            # Base64解码
            combined: bytes = base64.b64decode(encryptedBytes)

            # 拆分IV（前16字节）和密文
            iv: bytes = combined[:self.BLOCK_SIZE]
            ciphertext: bytes = combined[self.BLOCK_SIZE:]

            # 初始化解密器
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

            # 解密并去除填充
            decryptedBytes: bytes = cipher.decrypt(ciphertext)
            unpaddedData: bytes = unpad(decryptedBytes, self.BLOCK_SIZE, style="pkcs7")

            # 解码为字符串
            return unpaddedData.decode("utf-8")

        except (ValueError, IndexError) as e:
            # 填充错误或数据格式错误（最常见的解密失败原因）
            raise RuntimeError(f"解密失败（数据损坏或密钥错误）：{str(e)}")
        except Exception as e:
            raise RuntimeError(f"解密失败：{str(e)}")


# 测试代码
if __name__ == "__main__":
    # 测试1：使用默认密钥
    aes = AESHandler()
    testStr: str = "测试AES加密解密：包含特殊字符！@#$%^&*()，中文也没问题"
    encrypted: str = aes.encrypt(testStr)
    decrypted: str = aes.decrypt(encrypted)
    print(f"原始数据：{testStr}")
    print(f"加密后：{encrypted}")
    print(f"解密后：{decrypted}")
    print(f"解密是否一致：{decrypted == testStr}\n")

    # 测试2：使用自定义密钥
    customKey: str = AESHandler.generateRandomKey(128)  # 生成随机128位密钥
    print(f"自定义密钥：{customKey}")
    aesCustom = AESHandler(customKey)
    testJson: str = '{"name": "张三", "age": 25, "is_student": false}'
    encryptedJson: str = aesCustom.encrypt(testJson)
    decryptedJson: str = aesCustom.decrypt(encryptedJson)
    print(f"JSON解密是否一致：{decryptedJson == testJson}\n")

    # 测试3：异常情况（错误密钥解密）
    try:
        aesWrong = AESHandler("wrong_key_12345")  # 16字节的错误密钥
        aesWrong.decrypt(encrypted)
    except RuntimeError as e:
        print(f"预期异常：{e}")
