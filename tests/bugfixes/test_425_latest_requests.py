import requests
import httpretty


@httpretty.activate(allow_net_connect=True)
def test_latest_requests():
    "#425 - httpretty.latest_requests() can be called multiple times"
    httpretty.register_uri(httpretty.GET, 'http://google.com/', body="Not Google")
    httpretty.register_uri(httpretty.GET, 'https://google.com/', body="Not Google")

    assert httpretty.latest_requests() != []
    assert httpretty.latest_requests()[-1].url == 'http://google.com/'
    assert httpretty.latest_requests()[-1].url == 'http://google.com/'


    assert len(httpretty.latest_requests()) == 2
    assert httpretty.latest_requests()[-1].url == 'http://google.com/'

    requests.get('https://google.com/')
    assert len(httpretty.latest_requests()) == 3
    assert httpretty.latest_requests()[-1].url == 'http://google.com/'

    requests.get('http://google.com/')
    assert len(httpretty.latest_requests()) == 4
    assert httpretty.latest_requests()[-1].url == 'http://google.com/'
