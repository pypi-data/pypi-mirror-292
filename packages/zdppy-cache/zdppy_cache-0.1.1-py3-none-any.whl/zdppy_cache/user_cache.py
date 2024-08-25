import hashlib
import shutil
import os
import sys
from .core import Cache


class UserCache:
    def __init__(self, username, password, cache_dir="./tmp/.zdppy_cache"):
        # 构建缓存目录
        self.key = hashlib.sha256(f"{username}&&{password}".encode('utf-8')).hexdigest()
        self.cache_dir = os.path.join(cache_dir, self.key).replace("\\", "/")
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache = Cache(self.cache_dir)

    def set(self, key, value, expire=180):
        """设置缓存"""
        self.cache.set(key, value, expire)

    def get(self, key):
        """获取缓存"""
        value = self.cache.get(key)
        return value

    def delete_all(self):
        """清空缓存"""
        self.cache.close()
        try:
            shutil.rmtree(self.cache_dir)
        except OSError:
            pass

    def delete(self, key):
        """
        根据key删除缓存
        :param key: 缓存的key
        :return:
        """
        return self.cache.delete(key)

    def get_all_keys(self, is_active=True):
        """
        获取所有的key
        :param is_active: 默认只查询未过期的，传False则查询所有，包括已过期的。
        :return:
        """
        return self.cache.get_all_keys(is_active=is_active)

    def get_all_items(self, is_active=True):
        """
        获取所有的key-value键值对
        :param is_active: 默认只查询未过期的，传False则查询所有，包括已过期的。
        :return:
        """
        return self.cache.get_all_items(is_active=is_active)

    def get_all(self, is_active=True):
        """
        获取所有的缓存详细信息，返回的是列表字典
        :param is_active: 默认只查询未过期的，传False则查询所有，包括已过期的。
        :return:
        """
        return self.cache.get_all(is_active=is_active)

    def get_memory(self):
        """
        获取占据的内存大小
        但是只有在调用方法的那一刻会占据内存，平时都是存储在磁盘中的
        """
        return sys.getsizeof(self.cache)

    def get_size(self):
        """
        获取占据的内存大小
        但是只有在调用方法的那一刻会占据内存，平时都是存储在磁盘中的
        """
        return self.cache.volume()
