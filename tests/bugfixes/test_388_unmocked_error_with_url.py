# <HTTPretty - HTTP client mock for Python>
# Copyright (C) <2011-2021> Gabriel Falcão <gabriel@nacaolivre.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
import pytest
import requests
import httpretty
from httpretty.errors import UnmockedError


def http():
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    return sess


@httpretty.activate(allow_net_connect=False)
def test_https_forwarding():
    "#388 UnmockedError is raised with details about the mismatched request"
    httpretty.register_uri(httpretty.GET, 'http://google.com/', body="Not Google")
    httpretty.register_uri(httpretty.GET, 'https://google.com/', body="Not Google")
    response1 = http().get('http://google.com/')
    response2 = http().get('https://google.com/')

    with pytest.raises(UnmockedError, match=r'.*https://github.com/gabrielfalcao/HTTPretty.*') as exc_info:
        http().get("https://github.com/gabrielfalcao/HTTPretty")

    assert response1.text == response2.text
    try:
        http().get("https://github.com/gabrielfalcao/HTTPretty")
    except UnmockedError as exc:
        assert hasattr(exc, 'request')
        assert hasattr(exc.request, 'host') and exc.request.host == 'github.com'
        assert hasattr(exc.request, 'protocol') and exc.request.protocol == 'https'
        assert hasattr(exc.request, 'url') and exc.request.url == 'https://github.com/gabrielfalcao/HTTPretty'
