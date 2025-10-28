# -*- coding:utf-8 -*-
import hashlib
import base64
import json
from Crypto.Cipher import AES as CryptoAES
from Crypto.Util.Padding import pad

AES_KEY = "okmnhytfcde2025^"


class AES:
    def __init__(self, aes_key: str = None):
        self.key = aes_key if aes_key else AES_KEY

    # aes md5 添加固定字符串
    def aesMD5(self, md5_str):
        md5 = hashlib.md5()
        md5.update(md5_str.encode("utf-8"))
        return md5.hexdigest().upper()

    # aes 加密
    def Encryption(self, aes_str):
        # 使用 key，选择加密方式
        aes = CryptoAES.new(self.key.encode("utf-8"), CryptoAES.MODE_ECB)
        pad_pkcs7 = pad(
            aes_str.encode("utf-8"), CryptoAES.block_size, style="pkcs7"
        )  # 选择 pkcs7 补全
        encrypt_aes = aes.encrypt(pad_pkcs7)
        # 加密结果
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding="utf-8")  # 解码
        encrypted_text_str = encrypted_text.replace("\n", "")
        return encrypted_text_str

    # aes 解码
    def Decryption(self, aes_str):
        aes = CryptoAES.new(self.key.encode("utf-8"), CryptoAES.MODE_ECB)
        # 优先逆向解密 base64 成 bytes
        base64_decrypted = base64.decodebytes(aes_str.encode(encoding="utf-8-sig"))
        decrypted_text = (
            str(aes.decrypt(base64_decrypted), encoding="utf-8-sig")
            .replace("", "")
            .replace("", "")
        )
        # 注意这里解密会产生乱码，所以加密数据时可以用正则匹配掉乱码，具体问题具体对待
        # 这里传输的是 json 字符可以用这种方式匹配
        # print(decrypted_text)
        # decrypted_text=re.findall(".*\}",decrypted_text)[0]
        # decrypted_text = re.findall(".*\]", decrypted_text)[0]
        return decrypted_text


if __name__ == "__main__":

    data = [
        {
            "id": 1,
            "title": "西游记传",
            "author": "吴承恩",
            "price": "47.87",
            "pub_date": "2012-11-16",
            "publish": "中华出版社",
            "explain": "",
            "create_time": "2021-11-16 18:22:27",
        }
    ]
    print("源数据：", data)
    print("\n", "===" * 30, "\n")
    aes_Encryption = AES().Encryption(json.dumps(data))
    aes_Decryption = AES().Decryption(aes_Encryption)
    print("AES 加密：", aes_Encryption, "\n")
    print("AES 解密：", json.loads(aes_Decryption), "\n")
