# -*- coding:utf-8 -*-
import datetime
import jwt

JWT_KET = f"*9f0-b88xb%b=z$+md7h^1ey4-!fr!9eaj_cfg65g3g1l%$0o"


class JWT:
    def __init__(self, jwt_key: str = None):
        self.SECRECT_KEY = jwt_key if jwt_key else JWT_KET

    # 生成 jwt 信息，加密
    def jwtEncoding(self, data, some="webkit"):
        datetimes = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        option = {"data": data, "some": some, "datetime": datetimes}
        jwtencode = jwt.encode(option, self.SECRECT_KEY, algorithm="HS256")
        return jwtencode

    # 解密 jwt 信息
    def jwtDecoding(self, token):
        try:
            decoded = jwt.decode(token, self.SECRECT_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            decoded = {"error_msg": "is timeout !!", "some": None}
        except Exception:
            decoded = {"error_msg": "noknow exception!!", "some": None}
        return decoded


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
    jwtencode = JWT().jwtEncoding(data)
    jwtdeode = JWT().jwtDecoding(jwtencode)
    print("JWT 加密：", jwtencode, "\n", type(jwtencode))
    print("jwt 解密：", jwtdeode, "\n")
