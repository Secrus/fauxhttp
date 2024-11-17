# This test is based on @mariojonke snippet:
# https://github.com/gabrielfalcao/HTTPretty/issues/430
import time
import warnings

import pytest
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ReadTimeout

from threading import Event

from httpretty import httprettified
from httpretty import HTTPretty


def http(max_connections=1):
    session = Session()
    adapter = HTTPAdapter(
        pool_connections=max_connections,
        pool_maxsize=max_connections
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session



@httprettified(verbose=True, allow_net_connect=False)
def test_read_timeout():
    "#430 httpretty should respect read timeout"
    event = Event()
    uri = "http://example.com"

    #  Given that I register a uri with a callback body that delays 10 seconds
    wait_seconds = 10

    def my_callback(request, url, headers):
        event.wait(wait_seconds)
        return 200, headers, "Received"

    HTTPretty.register_uri(HTTPretty.GET, uri, body=my_callback)

    # And I use a thread pool with 1 TCP connection max
    max_connections = 1
    request = http(max_connections)
    started_at = time.time()

    with pytest.raises(ReadTimeout):
        request.get(uri, timeout=0.1)

    event.set()
    total_time = time.time() - started_at
    assert total_time < 0.2
