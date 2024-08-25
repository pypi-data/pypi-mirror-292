import shutil
import sys
from .core import Cache

# 默认缓存对象，上限520M
cache_directory = "tmp/.zdppy_cache"


def set(key, value, expire=180):
    """
    设置缓存
    @param expire 默认过期时间，单位秒，默认180，也就是3分钟
    :return:
    """
    # 设置缓存
    with Cache(cache_directory) as cache:
        return cache.set(key, value, expire=expire)


def get(key):
    """
    根据key获取缓存
    :param key: 缓存的key
    :return:
    """
    with Cache(cache_directory) as cache:
        return cache.get(key)


def delete(key):
    """
    根据key删除缓存
    :param key: 缓存的key
    :return:
    """
    with Cache(cache_directory) as cache:
        return cache.delete(key)


def delete_all():
    """
    删除所有的缓存
    :return:
    """
    try:
        shutil.rmtree(cache_directory)
    except OSError:
        pass


def get_all_keys(is_active=True):
    """
    获取所有的key
    :param is_active: 默认只查询未过期的，传False则查询所有，包括已过期的。
    :return:
    """
    with Cache(cache_directory) as cache:
        return cache.get_all_keys(is_active=is_active)


def get_all_items(is_active=True):
    """
    获取所有的key-value键值对
    :param is_active: 默认只查询未过期的，传False则查询所有，包括已过期的。
    :return:
    """
    with Cache(cache_directory) as cache:
        return cache.get_all_items(is_active=is_active)


def get_all(is_active=True):
    """
    获取所有的缓存详细信息，返回的是列表字典
    :param is_active: 默认只查询未过期的，传False则查询所有，包括已过期的。
    :return:
    """
    with Cache(cache_directory) as cache:
        return cache.get_all(is_active=is_active)


def get_memory():
    """
    获取占据的内存大小
    但是只有在调用方法的那一刻会占据内存，平时都是存储在磁盘中的
    """
    with Cache(cache_directory) as cache:
        return sys.getsizeof(cache)


def get_size():
    """
    获取占据的内存大小
    但是只有在调用方法的那一刻会占据内存，平时都是存储在磁盘中的
    """
    with Cache(cache_directory) as cache:
        return cache.volume()
