
import redis.asyncio as redis
import os
from contextlib import contextmanager, asynccontextmanager

if os.getenv('REDIS_URL', False):
    REDIS_URL = os.getenv('REDIS_URL')
else:
    REDIS_URL = 'redis://redis:6379'

EXPIRE = os.getenv('EXPIRE', 600)

redis_cli = None

@asynccontextmanager
async def close_redis():
    global redis_cli
    if redis_cli:
        redis_cli.close()
        await redis_cli.wait_closed()

@asynccontextmanager
async def get_redis():
    global redis_cli
    if not redis_cli:
        redis_cli = await redis.from_url(REDIS_URL)
    try:
        yield redis_cli
    finally:
        pass

async def check_token(samaccountname: str, token: str):
    async with get_redis() as redis:
        _token = await redis.get(f"token:{samaccountname}")
        if _token.decode('utf8') == str(token): 
            res = await redis.expire(f"token:{samaccountname}", xx=True, time=EXPIRE )
            if res:
                return res
    return False

async def create_token(samaccountname: str = '', token: str = ''):
    async with get_redis() as redis:
        res = await redis.set(f"token:{samaccountname}", token, ex=EXPIRE)
    return res

async def get_token(samaccountname: str):
    async with get_redis() as redis:
        token = await redis.get(f"token:{samaccountname}")  # Usa await aquí
        if token:
            return token
    return None
