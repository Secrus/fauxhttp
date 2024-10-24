import os
import requests
import httpretty
import pytest
try:
    from redis import Redis
except ImportError:
    Redis = None


def redis_available():
    if Redis is None:
        return False

    params = dict(
        host=os.getenv('REDIS_HOST') or '127.0.0.1',
        port=int(os.getenv('REDIS_PORT') or 6379)
    )
    conn = Redis(**params)
    try:
        conn.keys('*')
        conn.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not redis_available(), reason='no redis server available for test')
@httpretty.activate()
def test_work_in_parallel_to_redis():
    "HTTPretty should passthrough redis connections"

    redis = Redis()

    keys = redis.keys('*')
    for key in keys:
        redis.delete(key)

    redis.append('item1', 'value1')
    redis.append('item2', 'value2')

    assert sorted(redis.keys('*')) == [b'item1', b'item2']

    httpretty.register_uri(
        httpretty.GET,
        "http://redis.io",
        body="salvatore")

    response = requests.get('http://redis.io')
    assert response.text == 'salvatore'
