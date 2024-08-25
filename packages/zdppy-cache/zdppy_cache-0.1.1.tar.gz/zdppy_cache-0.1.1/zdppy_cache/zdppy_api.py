from .user_cache import UserCache


def cache(key1, key2, api):
    """
    生成缓存相关的接口
    :param key1: 管理员的第一个加密key
    :param key2: 管理员的第二个加密key
    :param api: zdppy_api 的包
    :return:
    """
    # 管理员的缓存对象
    admin_cache = UserCache(key1, key2)

    async def set(req):
        """设置缓存的接口"""
        data = await api.req.get_json(req)
        key = data.get("key")
        value = data.get("value")
        expire = data.get("expire")
        if not expire:
            expire = 180
        admin_cache.set(key, value, expire)
        return api.resp.success()

    async def get(req):
        """获取缓存的接口"""
        data = await api.req.get_json(req)
        key = data.get("key")
        value = admin_cache.get(key)
        return api.resp.success({"key": key, "value": value})

    # 缓存相关的接口
    return [
        api.resp.post("/zdppy_cache/set", set),
        api.resp.get("/zdppy_cache/get", get),
    ]
