# import httpretty
# import requests
# import eventlet
# eventlet.monkey_patch(all=False, socket=True)
#
#
# @httpretty.activate
# def test_something():
#     httpretty.register_uri(httpretty.GET, 'https://example.com', body='foo')
#     assert requests.get('https://example.com').text == 'foo'
