# zdppy_cache

Python的缓存库

## 使用教程

### 基本用法

```python
import zdppy_cache as c

# 设置缓存
key = "code"
value = "A13k"
c.set(key, value)

# 获取缓存
print(c.get(key))

# 删除缓存
c.delete(key)
print(c.get(key))

# 清空缓存
c.delete_all()
```

### 查询所有的key

默认参数是False，查询所有未过期的。传True则查询所有，包括已过期的。

```python
import zdppy_cache as c
import time

# 设置缓存
key = "code"
value = "A13k"
c.set(key, value, 3)

# 获取所有的缓存的key
print(c.get_all_keys())

time.sleep(3)
print("默认查询未过期的：", c.get_all_keys())
print("查询过期的：", c.get_all_keys(False))

# 清空缓存
c.delete_all()
```

### 查询所有的键值对

```python
import zdppy_cache as c
import time

# 设置缓存
key = "code"
value = "A13k"
c.set(key, value, 3)

# 获取所有的缓存的key-value
print(c.get_all_items())

time.sleep(3)
print("默认查询未过期的：", c.get_all_items())
print("查询过期的：", c.get_all_items(False))

# 清空缓存
c.delete_all()

```

### 查询所有的有效具体数据

会返回具体详细的缓存信息。

```python
import zdppy_cache as c
import time

# 设置缓存
key = "code"
value = "A13k"
c.set(key, value, 3)

# 获取所有的缓存的key-value
print(c.get_all())

time.sleep(3)
print("默认查询未过期的：", c.get_all())
print("查询过期的：", c.get_all(False))

# 清空缓存
c.delete_all()
```

### 获取缓存文件大小

```python
import zdppy_cache as c
import time

# 设置缓存
key = "code"
value = "A13k"
c.set(key, value, 3)

# 获取占据磁盘大小
print(c.get_size())

# 加很多东西
for i in range(100):
    c.set(f"zhangsan{i}", i)

print(c.get_size())

# 清空缓存
c.delete_all()
```

### 通过账号密码区分用户的缓存

```python
import zdppy_cache

# 设置缓存
key = "code"
value = "A13k"

# 设置缓存
c = zdppy_cache.UserCache("admin", "admin123456")
c.set(key, value, 3)

# 获取缓存
print(c.get(key))

# 让另一个用户去获取缓存
c = zdppy_cache.UserCache("admin", "admin123457")
print("另一个用户", c.get(key))

# 清空缓存
c.delete_all()
```

### 基于zdppy_api实现的接口级别的缓存

```python
import api
import zdppy_cache

key1 = "admin"
key2 = "admin123456"
app = api.Api(
    routes=[
        *zdppy_cache.zdppy_api.cache(key1, key2, api)
    ]
)

if __name__ == '__main__':
    app.run()
```

设置缓存：

```bash
req -X POST -d '{\"key\":1,\"value\":111}' http://127.0.0.1:8888/zdppy_cache/set
```

获取缓存：

```bash
req -d '{\"key\":1}' http://127.0.0.1:8888/zdppy_cache/get
```

## 版本历史

### v0.1.1

- 支持zpppy_api接口级别的缓存
