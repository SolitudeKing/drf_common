from redis import Redis
from django_redis import get_redis_connection
# 连接到默认的Redis数据库
redis: Redis = get_redis_connection("default")
# job_redis: Redis = get_redis_connection("job")
import json
import pickle


class CommCache:
    """
    通用缓存类，提供对Redis缓存的基本操作。
    """
    @classmethod
    def dataProcess(cls, data: any, pick_ser: bool = False, json_ser: bool = False, method: str = None) -> any:
        """
        根据指定的序列化方法处理数据。
        :param data: 要处理的数据
        :param pick_ser: 是否使用pickle序列化
        :param json_ser: 是否使用json序列化
        :param method: 序列化方法（dumps或loads）
        :return: 处理后的数据
        """
        if pick_ser:
            return getattr(pickle, method)(data)
        elif json_ser:
            return getattr(json, method)(data)
        return data

    @classmethod
    def delete(cls, cache_key: str) -> None:
        """
        删除缓存中的数据。
        :param new_key: 要删除的键
        """
        redis.delete(cache_key)

    @classmethod
    def ttl(cls, cache_key: str) -> int:
        """
        获取缓存数据的剩余生存时间。
        :param key: 缓存键
        :return: 剩余生存时间（秒）
        """
        return redis.ttl(cache_key)

    @classmethod
    def get(cls, cache_key: str, pick_ser: bool = False, json_ser: bool = False) -> any:
        """
        从缓存中获取数据。
        :param key: 缓存键
        :param pick_ser: 是否使用pickle反序列化
        :param json_ser: 是否使用json反序列化
        :return: 获取的数据
        """
        data = redis.get(cache_key)

        if data:
            data = cls.dataProcess(data, pick_ser=pick_ser, json_ser=json_ser, method="loads")
        return data

    @classmethod
    def set(cls, cache_key: str, data: any, timeout: int = None, pick_ser: bool = False, json_ser: bool = False) -> None:
        """
        设置缓存数据。
        :param data: 要缓存的数据
        :param timeout: 过期时间（秒）
        :param new_key: 缓存键
        :param pick_ser: 是否使用pickle序列化
        :param json_ser: 是否使用json序列化
        """
        data = cls.dataProcess(data, pick_ser=pick_ser, json_ser=json_ser, method="dumps")

        if timeout:
            redis.set(cache_key, data, ex=timeout)
        else:
            redis.set(cache_key, data)

    @classmethod
    def sadd(cls, cache_key: str, *value: any) -> None:
        """
        向集合添加一个或多个成员。
        :param value: 要添加的成员
        :param key: 集合键
        """
        redis.sadd(cache_key, *value)

    @classmethod
    def sismember(cls, cache_key: str, value: any) -> bool:
        """
        判断成员是否是集合的成员。
        :param value: 要判断的成员
        :param key: 集合键
        :return: 是否是集合的成员
        """
        result = redis.sismember(cache_key, value)
        return result


def redisExist(key: str, time: int, value: int = 1) -> bool:
    """
    判断Redis中是否存在指定键，如果不存在则设置键值并设置过期时间。
    :param key: 键
    :param time: 过期时间（秒）
    :param value: 键值
    :return: 是否存在
    """
    if redis.exists(key):
        return True
    redis.set(key, value, time)
    return False
