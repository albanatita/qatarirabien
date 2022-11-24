import redis

r = redis.StrictRedis(host='localhost', port=6379, db=1)
print("set key1 123")
print(r.set('key1', '123'))
print("get key1")
print(r.get('key1'))
