import httpretty
import requests


@httpretty.activate
def test_test_ssl_bad_handshake():
    # Reproduces https://github.com/gabrielfalcao/HTTPretty/issues/242

    url_http = 'http://httpbin.org/status/200'
    url_https = 'https://github.com/gabrielfalcao/HTTPretty'

    httpretty.register_uri(httpretty.GET, url_http, body='insecure')
    httpretty.register_uri(httpretty.GET, url_https, body='encrypted')

    assert requests.get(url_http).text == 'insecure'
    assert requests.get(url_https).text == 'encrypted'

    httpretty.latest_requests().should.have.length_of(2)
    insecure_request, secure_request = httpretty.latest_requests()[:2]

    assert insecure_request.protocol == 'http'
    assert secure_request.protocol == 'https'

    assert insecure_request.url == url_http
    assert secure_request.url == url_https
