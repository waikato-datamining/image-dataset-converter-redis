import redis
from dataclasses import dataclass


@dataclass
class RedisSession:
    connection: redis.Redis = None
