# based on the snippet from https://github.com/gabrielfalcao/HTTPretty/issues/387
import httpretty
import requests


@httpretty.activate(allow_net_connect=False, verbose=True)
def test_match_with_port_no_slashes():
    "Reproduce #387 registering host:port without trailing slash"
    httpretty.register_uri(httpretty.GET, 'http://fakeuri.com:8080', body='{"hello":"world"}')
    req = requests.get('http://fakeuri.com:8080', timeout=1)
    assert req.status_code == 200
    assert req.json() == {"hello": "world"}


@httpretty.activate(allow_net_connect=False, verbose=True)
def test_match_with_port_trailing_slash():
    "Reproduce #387 registering host:port with trailing slash"
    httpretty.register_uri(httpretty.GET, 'https://fakeuri.com:443/', body='{"hello":"world"}')
    req = requests.get('https://fakeuri.com:443', timeout=1)
    assert req.status_code == 200
    assert req.json() == {"hello": "world"}

    req = requests.get('https://fakeuri.com:443/', timeout=1)
    assert req.status_code == 200
    assert req.json() == {"hello": "world"}
