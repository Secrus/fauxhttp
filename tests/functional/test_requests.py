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

import os
import re
import json
import requests
import signal
import httpretty
import pytest
from freezegun import freeze_time
from contextlib import contextmanager
from tornado import version as tornado_version
from httpretty import HTTPretty, httprettified
from httpretty.core import decode_utf8
from unittest.mock import Mock

from tests.functional.base import FIXTURE_FILE, use_tornado_server


server_url = lambda path, port: "http://localhost:{}/{}".format(port, path.lstrip('/'))


@httprettified
#@within(two=miliseconds)
def test_httpretty_should_mock_a_simple_get_with_requests_read():
    "HTTPretty should mock a simple GET with requests.get"

    HTTPretty.register_uri(HTTPretty.GET, "http://yipit.com/",
                           body="Find the best daily deals")

    response = requests.get('http://yipit.com')
    assert response.text=='Find the best daily deals'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/'


@httprettified
#@within(two=miliseconds)
def test_hostname_case_insensitive():
    "HTTPretty should match the hostname case insensitive"

    HTTPretty.register_uri(HTTPretty.GET, "http://yipit/",
                           body="Find the best daily deals")

    response = requests.get('http://YIPIT')
    assert response.text=='Find the best daily deals'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/'


@httprettified
#@within(two=miliseconds)
def test_httpretty_provides_easy_access_to_querystrings():
    "HTTPretty should provide an easy access to the querystring"

    HTTPretty.register_uri(HTTPretty.GET, "http://yipit.com/",
                           body="Find the best daily deals")

    requests.get('http://yipit.com/?foo=bar&foo=baz&chuck=norris')
    assert HTTPretty.last_request.querystring == {
        'foo': ['bar', 'baz'],
        'chuck': ['norris'],
    }


@httprettified
@freeze_time("2013-10-04 04:20:00")
def test_httpretty_should_mock_headers_requests():
    "HTTPretty should mock basic headers with requests"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/",
                           body="this is supposed to be the response",
                           status=201)

    response = requests.get('http://github.com')
    assert response.status_code==201

    assert dict(response.headers) == {
        'content-type': 'text/plain; charset=utf-8',
        'connection': 'close',
        'content-length': '35',
        'status': '201',
        'server': 'Python/HTTPretty',
        'date': 'Fri, 04 Oct 2013 04:20:00 GMT',
    }


@httprettified
@freeze_time("2013-10-04 04:20:00")
def test_httpretty_should_allow_adding_and_overwritting_requests():
    "HTTPretty should allow adding and overwritting headers with requests"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/foo",
                           body="this is supposed to be the response",
                           adding_headers={
                               'Server': 'Apache',
                               'Content-Length': '27',
                               'Content-Type': 'application/json',
                           })

    response = requests.get('http://github.com/foo')

    assert dict(response.headers) == {
        'content-type': 'application/json',
        'connection': 'close',
        'content-length': '27',
        'status': '200',
        'server': 'Apache',
        'date': 'Fri, 04 Oct 2013 04:20:00 GMT',
    }


@httprettified
#@within(two=miliseconds)
def test_httpretty_should_allow_forcing_headers_requests():
    "HTTPretty should allow forcing headers with requests"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/foo",
                           body="<root><baz /</root>",
                           forcing_headers={
                               'Content-Type': 'application/xml',
                               'Content-Length': '19',
                           })

    response = requests.get('http://github.com/foo')

    assert dict(response.headers) == {
        'content-type': 'application/xml',
        'content-length': '19',
    }


@httprettified
@freeze_time("2013-10-04 04:20:00")
def test_httpretty_should_allow_adding_and_overwritting_by_kwargs_u2():
    "HTTPretty should allow adding and overwritting headers by keyword args " \
        "with requests"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/foo",
                           body="this is supposed to be the response",
                           server='Apache',
                           content_length='27',
                           content_type='application/json')

    response = requests.get('http://github.com/foo')

    assert dict(response.headers) == {
        'content-type': 'application/json',
        'connection': 'close',
        'content-length': '27',
        'status': '200',
        'server': 'Apache',
        'date': 'Fri, 04 Oct 2013 04:20:00 GMT',
    }


@httprettified
#@within(two=miliseconds)
def test_rotating_responses_with_requests():
    "HTTPretty should support rotating responses with requests"

    HTTPretty.register_uri(
        HTTPretty.GET, "https://api.yahoo.com/test",
        responses=[
            HTTPretty.Response(body=b"first response", status=201),
            HTTPretty.Response(body=b'second and last response', status=202),
        ])

    response1 = requests.get(
        'https://api.yahoo.com/test')

    assert response1.status_code==201
    assert response1.text=='first response'

    response2 = requests.get(
        'https://api.yahoo.com/test')

    assert response2.status_code==202
    assert response2.text=='second and last response'

    response3 = requests.get(
        'https://api.yahoo.com/test')

    assert response3.status_code==202
    assert response3.text=='second and last response'


@httprettified
#@within(two=miliseconds)
def test_can_inspect_last_request():
    "HTTPretty.last_request is a mimetools.Message request from last match"

    HTTPretty.register_uri(HTTPretty.POST, "http://api.github.com/",
                           body='{"repositories": ["HTTPretty", "lettuce"]}')

    response = requests.post(
        'http://api.github.com',
        '{"username": "gabrielfalcao"}',
        headers={
            'content-type': 'text/json',
        },
    )

    assert HTTPretty.last_request.method=='POST'
    assert HTTPretty.last_request.body == b'{"username": "gabrielfalcao"}'
    assert HTTPretty.last_request.headers['content-type'] == 'text/json'
    assert response.json()=={"repositories": ["HTTPretty", "lettuce"]}


@httprettified
#@within(two=miliseconds)
def test_can_inspect_last_request_with_ssl():
    "HTTPretty.last_request is recorded even when mocking 'https' (SSL)"

    HTTPretty.register_uri(HTTPretty.POST, "https://secure.github.com/",
                           body='{"repositories": ["HTTPretty", "lettuce"]}')

    response = requests.post(
        'https://secure.github.com',
        '{"username": "gabrielfalcao"}',
        headers={
            'content-type': 'text/json',
        },
    )

    assert HTTPretty.last_request.method=='POST'
    assert HTTPretty.last_request.body == b'{"username": "gabrielfalcao"}'
    assert HTTPretty.last_request.headers['content-type'] == 'text/json'
    assert response.json()=={"repositories": ["HTTPretty", "lettuce"]}


@httprettified
#@within(two=miliseconds)
def test_httpretty_ignores_querystrings_from_registered_uri():
    "HTTPretty should ignore querystrings from the registered uri (requests library)"

    HTTPretty.register_uri(HTTPretty.GET, "http://yipit.com/?id=123",
                           body=b"Find the best daily deals")

    response = requests.get('http://yipit.com/', params={'id': 123})
    assert response.text=='Find the best daily deals'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/?id=123'


@httprettified
#@within(five=miliseconds)
def test_streaming_responses():
    """
    Mock a streaming HTTP response, like those returned by the Twitter streaming
    API.
    """

    @contextmanager
    def in_time(time, message):
        """
        A context manager that uses signals to force a time limit in tests
        (unlike the `@within` decorator, which only complains afterward), or
        raise an AssertionError.
        """
        def handler(signum, frame):
            raise AssertionError(message)
        signal.signal(signal.SIGALRM, handler)
        signal.setitimer(signal.ITIMER_REAL, time)
        yield
        signal.setitimer(signal.ITIMER_REAL, 0)

    # XXX this obviously isn't a fully functional twitter streaming client!
    twitter_response_lines = [
        b'{"text":"If \\"for the boobs\\" requests to follow me one more time I\'m calling the police. http://t.co/a0mDEAD8"}\r\n',
        b'\r\n',
        b'{"text":"RT @onedirection: Thanks for all your # FollowMe1D requests Directioners! We\u2019ll be following 10 people throughout the day starting NOW. G ..."}\r\n'
    ]

    TWITTER_STREAMING_URL = "https://stream.twitter.com/1/statuses/filter.json"

    HTTPretty.register_uri(HTTPretty.POST, TWITTER_STREAMING_URL,
                           body=(l for l in twitter_response_lines),
                           streaming=True)

    # taken from the requests docs

    # test iterating by line
    # Http://docs.python-requests.org/en/latest/user/advanced/# streaming-requests
    response = requests.post(TWITTER_STREAMING_URL, data={'track': 'requests'},
                             auth=('username', 'password'), stream=True)

    line_iter = response.iter_lines()
    with in_time(0.01, 'Iterating by line is taking forever!'):
        for i in range(len(twitter_response_lines)):
            assert next(line_iter).strip()== twitter_response_lines[i].strip()

    HTTPretty.register_uri(HTTPretty.POST, TWITTER_STREAMING_URL,
                           body=(l for l in twitter_response_lines),
                           streaming=True)
    # test iterating by line after a second request
    response = requests.post(
        TWITTER_STREAMING_URL,
        data={
            'track': 'requests'
        },
        auth=('username', 'password'),
        stream=True,
    )

    line_iter = response.iter_lines()
    with in_time(0.01, 'Iterating by line is taking forever the second time '
                       'around!'):
        for i in range(len(twitter_response_lines)):
            assert next(line_iter).strip()== twitter_response_lines[i].strip()

    HTTPretty.register_uri(HTTPretty.POST, TWITTER_STREAMING_URL,
                           body=(l for l in twitter_response_lines),
                           streaming=True)
    # test iterating by char
    response = requests.post(
        TWITTER_STREAMING_URL,
        data={
            'track': 'requests'
        },
        auth=('username', 'password'),
        stream=True
    )

    twitter_expected_response_body = b''.join(twitter_response_lines)
    with in_time(0.02, 'Iterating by char is taking forever!'):
        twitter_body = b''.join(c for c in response.iter_content(chunk_size=1))

    assert twitter_body == twitter_expected_response_body

    # test iterating by chunks larger than the stream
    HTTPretty.register_uri(HTTPretty.POST, TWITTER_STREAMING_URL,
                           body=(l for l in twitter_response_lines),
                           streaming=True)
    response = requests.post(TWITTER_STREAMING_URL, data={'track': 'requests'},
                             auth=('username', 'password'), stream=True)

    with in_time(0.02, 'Iterating by large chunks is taking forever!'):
        twitter_body = b''.join(c for c in
                                response.iter_content(chunk_size=1024))

    assert twitter_body==twitter_expected_response_body


@httprettified
def test_multiline():
    url = 'https://httpbin.org/post'
    data = b'content=Im\r\na multiline\r\n\r\nsentence\r\n'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Accept': 'text/plain',
    }
    HTTPretty.register_uri(
        HTTPretty.POST,
        url,
    )
    response = requests.post(url, data=data, headers=headers)

    assert response.status_code==200
    assert HTTPretty.last_request.method=='POST'
    assert HTTPretty.last_request.url=='https://httpbin.org/post'
    assert HTTPretty.last_request.protocol=='https'
    assert HTTPretty.last_request.path=='/post'
    assert HTTPretty.last_request.body==data
    assert HTTPretty.last_request.headers['content-length']=='37'
    assert HTTPretty.last_request.headers['content-type']=='application/x-www-form-urlencoded; charset=utf-8'
    assert len(HTTPretty.latest_requests)==1


@httprettified
def test_octet_stream():
    url = 'https://httpbin.org/post'
    data = b"\xf5\x00\x00\x00"  # utf-8 with invalid start byte
    headers = {
        'Content-Type': 'application/octet-stream',
    }
    HTTPretty.register_uri(
        HTTPretty.POST,
        url,
    )
    response = requests.post(url, data=data, headers=headers)

    assert response.status_code==200
    assert HTTPretty.last_request.method=='POST'
    assert HTTPretty.last_request.url=='https://httpbin.org/post'
    assert HTTPretty.last_request.protocol=='https'
    assert HTTPretty.last_request.path=='/post'
    assert HTTPretty.last_request.body==data
    assert HTTPretty.last_request.headers['content-length']=='4'
    assert HTTPretty.last_request.headers['content-type']=='application/octet-stream'
    assert len(HTTPretty.latest_requests)==1


@httprettified
def test_multipart():
    url = 'https://httpbin.org/post'
    data = b'--xXXxXXyYYzzz\r\nContent-Disposition: form-data; name="content"\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 68\r\n\r\nAction: comment\nText: Comment with attach\nAttachment: x1.txt, x2.txt\r\n--xXXxXXyYYzzz\r\nContent-Disposition: form-data; name="attachment_2"; filename="x.txt"\r\nContent-Type: text/plain\r\nContent-Length: 4\r\n\r\nbye\n\r\n--xXXxXXyYYzzz\r\nContent-Disposition: form-data; name="attachment_1"; filename="x.txt"\r\nContent-Type: text/plain\r\nContent-Length: 4\r\n\r\nbye\n\r\n--xXXxXXyYYzzz--\r\n'
    headers = {'Content-Length': '495', 'Content-Type': 'multipart/form-data; boundary=xXXxXXyYYzzz', 'Accept': 'text/plain'}
    HTTPretty.register_uri(
        HTTPretty.POST,
        url,
    )
    response = requests.post(url, data=data, headers=headers)
    assert response.status_code==200
    assert HTTPretty.last_request.method=='POST'
    assert HTTPretty.last_request.url=='https://httpbin.org/post'
    assert HTTPretty.last_request.protocol=='https'
    assert HTTPretty.last_request.path=='/post'
    assert HTTPretty.last_request.body==data
    assert HTTPretty.last_request.headers['content-length']=='495'
    assert HTTPretty.last_request.headers['content-type']=='multipart/form-data; boundary=xXXxXXyYYzzz'
    assert len(HTTPretty.latest_requests)==1


@httprettified
#@within(two=miliseconds)
def test_callback_response():
    ("HTTPretty should call a callback function and set its return value as the body of the response"
     " requests")

    def request_callback(request, uri, headers):
        return [200, headers, "The {} response from {}".format(decode_utf8(request.method), uri)]

    HTTPretty.register_uri(
        HTTPretty.GET, "https://api.yahoo.com/test",
        body=request_callback)

    response = requests.get('https://api.yahoo.com/test')

    assert response.text=="The GET response from https://api.yahoo.com/test"

    HTTPretty.register_uri(
        HTTPretty.POST, "https://api.yahoo.com/test_post",
        body=request_callback)

    response = requests.post(
        "https://api.yahoo.com/test_post",
        {"username": "gabrielfalcao"}
    )

    assert response.text=="The POST response from https://api.yahoo.com/test_post"


@httprettified
#@within(two=miliseconds)
def test_callback_body_remains_callable_for_any_subsequent_requests():
    ("HTTPretty should call a callback function more than one"
     " requests")

    def request_callback(request, uri, headers):
        return [200, headers, "The {} response from {}".format(decode_utf8(request.method), uri)]

    HTTPretty.register_uri(
        HTTPretty.GET, "https://api.yahoo.com/test",
        body=request_callback)

    response = requests.get('https://api.yahoo.com/test')
    assert response.text=="The GET response from https://api.yahoo.com/test"

    response = requests.get('https://api.yahoo.com/test')
    assert response.text=="The GET response from https://api.yahoo.com/test"


@httprettified
#@within(two=miliseconds)
def test_callback_setting_headers_and_status_response():
    ("HTTPretty should call a callback function and uses it retur tuple as status code, headers and body"
     " requests")

    def request_callback(request, uri, headers):
        headers.update({'a': 'b'})
        return [418, headers, "The {} response from {}".format(decode_utf8(request.method), uri)]

    HTTPretty.register_uri(
        HTTPretty.GET, "https://api.yahoo.com/test",
        body=request_callback)

    response = requests.get('https://api.yahoo.com/test')
    assert response.text=="The GET response from https://api.yahoo.com/test"
    assert response.headers['a'] == 'b'
    assert response.status_code==418

    HTTPretty.register_uri(
        HTTPretty.POST, "https://api.yahoo.com/test_post",
        body=request_callback)

    response = requests.post(
        "https://api.yahoo.com/test_post",
        {"username": "gabrielfalcao"}
    )

    assert response.text=="The POST response from https://api.yahoo.com/test_post"
    assert response.headers['a'] == 'b'
    assert response.status_code==418


@httprettified
def test_httpretty_should_respect_matcher_priority():
    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r".*"),
        body='high priority',
        priority=5,
    )
    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r".+"),
        body='low priority',
        priority=0,
    )
    response = requests.get('http://api.yipit.com/v1/')
    assert response.text=='high priority'


@httprettified
#@within(two=miliseconds)
def test_callback_setting_content_length_on_head():
    ("HTTPretty should call a callback function, use it's return tuple as status code, headers and body"
     " requests and respect the content-length header when responding to HEAD")

    def request_callback(request, uri, headers):
        headers.update({'content-length': 12345})
        return [200, headers, ""]

    HTTPretty.register_uri(
        HTTPretty.HEAD, "https://api.yahoo.com/test",
        body=request_callback)

    response = requests.head('https://api.yahoo.com/test')
    assert response.headers['content-length'] == "12345"
    assert response.status_code==200


@httprettified
def test_httpretty_should_allow_registering_regexes_and_give_a_proper_match_to_the_callback():
    "HTTPretty should allow registering regexes with requests and giva a proper match to the callback"

    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r"https://api.yipit.com/v1/deal;brand=(?P<brand_name>\w+)"),
        body=lambda method, uri, headers: [200, headers, uri]
    )

    response = requests.get('https://api.yipit.com/v1/deal;brand=gap?first_name=chuck&last_name=norris')

    assert response.text=='https://api.yipit.com/v1/deal;brand=gap?first_name=chuck&last_name=norris'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/v1/deal;brand=gap?first_name=chuck&last_name=norris'


@httprettified
def test_httpretty_should_allow_registering_regexes():
    "HTTPretty should allow registering regexes with requests"

    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r"https://api.yipit.com/v1/deal;brand=(?P<brand_name>\w+)"),
        body="Found brand",
    )

    response = requests.get('https://api.yipit.com/v1/deal;brand=gap?first_name=chuck&last_name=norris'
                            )
    assert response.text=='Found brand'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/v1/deal;brand=gap?first_name=chuck&last_name=norris'


@httprettified
def test_httpretty_provides_easy_access_to_querystrings_with_regexes():
    "HTTPretty should match regexes even if they have a different querystring"

    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r"https://api.yipit.com/v1/(?P<endpoint>\w+)/$"),
        body="Find the best daily deals"
    )

    response = requests.get('https://api.yipit.com/v1/deals/?foo=bar&foo=baz&chuck=norris')
    assert response.text=="Find the best daily deals"
    assert HTTPretty.last_request.querystring == {
        'foo': ['bar', 'baz'],
        'chuck': ['norris'],
    }


@httprettified(verbose=True)
def test_httpretty_allows_to_chose_if_querystring_should_be_matched():
    "HTTPretty should provide a way to not match regexes that have a different querystring"

    HTTPretty.register_uri(
        HTTPretty.GET,
        "http://localhost:9090",
    )
    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r"http://localhost:9090/what/?$"),
        body="Nudge, nudge, wink, wink. Know what I mean?",
        match_querystring=True
    )
    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r"http://localhost:9090/what.*[?]?.*"),
        body="Different",
        match_querystring=False
    )
    response = requests.get('http://localhost:9090/what/')
    assert response.text=='Nudge, nudge, wink, wink. Know what I mean?'

    response = requests.get('http://localhost:9090/what/', params={'flying': 'coconuts'})
    assert response.text =='Nudge, nudge, wink, wink. Know what I mean?'


@httprettified
def test_httpretty_should_allow_multiple_methods_for_the_same_uri():
    "HTTPretty should allow registering multiple methods for the same uri"

    url = 'http://test.com/test'
    methods = ['GET', 'POST', 'PUT', 'OPTIONS']
    for method in methods:
        HTTPretty.register_uri(
            getattr(HTTPretty, method),
            url,
            method
        )

    for method in methods:
        request_action = getattr(requests, method.lower())
        assert request_action(url).text==method


@httprettified
def test_httpretty_should_allow_registering_regexes_with_streaming_responses():
    "HTTPretty should allow registering regexes with streaming responses"

    os.environ['DEBUG'] = 'true'

    def my_callback(request, url, headers):

        if requests.__version__ < "2.29":
            assert request.body == b'hithere'
        else:
            assert request.body == b'2\r\nhi\r\n5\r\nthere\r\n'
        return 200, headers, "Received"

    HTTPretty.register_uri(
        HTTPretty.POST,
        re.compile(r"https://api.yipit.com/v1/deal;brand=(?P<brand_name>\w+)"),
        body=my_callback,
    )

    def gen():
        yield b'hi'
        yield b'there'

    response = requests.post(
        'https://api.yipit.com/v1/deal;brand=gap?first_name=chuck&last_name=norris',
        data=gen(),
    )
    assert response.content==b"Received"
    assert HTTPretty.last_request.method=='POST'
    assert HTTPretty.last_request.path=='/v1/deal;brand=gap?first_name=chuck&last_name=norris'


@httprettified
def test_httpretty_should_allow_multiple_responses_with_multiple_methods():
    "HTTPretty should allow multiple responses when binding multiple methods to the same uri"

    url = 'http://test.com/list'

    # add get responses
    HTTPretty.register_uri(
        HTTPretty.GET, url,
        responses=[
            HTTPretty.Response(body='a'),
            HTTPretty.Response(body='b'),
        ]
    )

    # add post responses
    HTTPretty.register_uri(
        HTTPretty.POST, url,
        responses=[
            HTTPretty.Response(body='c'),
            HTTPretty.Response(body='d'),
        ]
    )

    assert requests.get(url).text=='a'
    assert requests.post(url).text=='c'

    assert requests.get(url).text=='b'
    assert requests.get(url).text=='b'
    assert requests.get(url).text=='b'

    assert requests.post(url).text=='d'
    assert requests.post(url).text=='d'
    assert requests.post(url).text=='d'


@httprettified
def test_httpretty_should_normalize_url_patching():
    "HTTPretty should normalize all url patching"

    HTTPretty.register_uri(
        HTTPretty.GET,
        "http://yipit.com/foo(bar)",
        body="Find the best daily deals")

    response = requests.get('http://yipit.com/foo%28bar%29')
    assert response.text=='Find the best daily deals'


@httprettified
def test_lack_of_trailing_slash():
    ("HTTPretty should automatically append a slash to given urls")
    url = 'http://www.youtube.com'
    HTTPretty.register_uri(HTTPretty.GET, url, body='')
    response = requests.get(url)
    assert response.status_code == 200


@httprettified
def test_unicode_querystrings():
    ("Querystrings should accept unicode characters")
    HTTPretty.register_uri(HTTPretty.GET, "http://yipit.com/login",
                           body="Find the best daily deals")
    requests.get('http://yipit.com/login?user=Gabriel+Falcão')
    assert HTTPretty.last_request.querystring['user'][0] == 'Gabriel Falcão'

#
# @use_tornado_server
# def test_recording_calls(port):
#     ("HTTPretty should be able to record calls")
#     # Given a destination path:
#     destination = FIXTURE_FILE("recording-1.json")
#
#     # When I record some calls
#     with HTTPretty.record(destination):
#         requests.get(server_url("/foobar?name=Gabriel&age=25", port))
#         requests.post(server_url("/foobar", port),
#                       data=json.dumps({'test': '123'}),
#                       headers={"Test": "foobar"})
#
#     # Then the destination path should exist
#     assert os.path.exists(destination)
#
#     # And the contents should be json
#     raw = open(destination).read()
#     #json.loads.when.called_with(raw).should_not.throw(ValueError)
#
#     # And the contents should be expected
#     data = json.loads(raw)
#     assert type(data) is list
#     assert len(data) == 2
#     # And the responses should have the expected keys
#     response = data[0]
#     assert len(response['request']) == 5
#     assert len(response['response']) == 3
#
#     assert response['request']['method'] == 'GET'
#     assert type(response['request']['headers']) is dict
#     assert response['request']['querystring'] == {
#         "age": [
#             "25"
#         ],
#         "name": [
#             "Gabriel"
#         ]
#     }
#     assert response['response']['status'] == 200
#     assert type(response['response']['body']) is str
#     assert type(response['response']['headers']) is dict
#     # older urllib3 had a bug where header keys were lower-cased:
#     # https://github.com/shazow/urllib3/issues/236
#     # cope with that
#     if 'server' in response['response']["headers"]:
#         response['response']["headers"]["Server"] = response['response']["headers"].pop("server")
#     assert response['response']["headers"]["Server"] == "TornadoServer/" + tornado_version
#
#     # And When I playback the previously recorded calls
#     with HTTPretty.playback(destination):
#         # And make the expected requests
#         response1 = requests.get(server_url("/foobar?name=Gabriel&age=25", port))
#         response2 = requests.post(
#             server_url("/foobar", port),
#             data=json.dumps({'test': '123'}),
#             headers={"Test": "foobar"},
#         )
#
#     # Then the responses should be the expected
#     assert response1.json()=={"foobar": {"age": "25", "name": "Gabriel"}}
#     assert response2.json()["foobar"]=={}
#     assert response2.json()["req_body"]==json.dumps({"test": "123"})
#     assert response2.json()["req_headers"]["Test"]
#     assert response2.json()["req_headers"]["Test"]=="foobar"


@httprettified
def test_httpretty_should_work_with_non_standard_ports():
    "HTTPretty should work with a non-standard port number"

    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r"https://api.yipit.com:1234/v1/deal;brand=(?P<brand_name>\w+)"),
        body=lambda method, uri, headers: [200, headers, uri]
    )
    HTTPretty.register_uri(
        HTTPretty.POST,
        "https://asdf.com:666/meow",
        body=lambda method, uri, headers: [200, headers, uri]
    )

    response = requests.get('https://api.yipit.com:1234/v1/deal;brand=gap?first_name=chuck&last_name=norris')

    assert response.text=='https://api.yipit.com:1234/v1/deal;brand=gap?first_name=chuck&last_name=norris'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/v1/deal;brand=gap?first_name=chuck&last_name=norris'

    response = requests.post('https://asdf.com:666/meow')

    assert response.text=='https://asdf.com:666/meow'
    assert HTTPretty.last_request.method=='POST'
    assert HTTPretty.last_request.path=='/meow'


@httprettified
def test_httpretty_reset_by_switching_protocols_for_same_port():
    "HTTPretty should reset protocol/port associations"

    HTTPretty.register_uri(
        HTTPretty.GET,
        "http://api.yipit.com:1234/v1/deal",
        body=lambda method, uri, headers: [200, headers, uri]
    )

    response = requests.get('http://api.yipit.com:1234/v1/deal')

    assert response.text=='http://api.yipit.com:1234/v1/deal'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/v1/deal'

    HTTPretty.reset()

    HTTPretty.register_uri(
        HTTPretty.GET,
        "https://api.yipit.com:1234/v1/deal",
        body=lambda method, uri, headers: [200, headers, uri]
    )

    response = requests.get('https://api.yipit.com:1234/v1/deal')

    assert response.text=='https://api.yipit.com:1234/v1/deal'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/v1/deal'


@httprettified
def test_httpretty_should_allow_registering_regexes_with_port_and_give_a_proper_match_to_the_callback():
    "HTTPretty should allow registering regexes with requests and giva a proper match to the callback"

    HTTPretty.register_uri(
        HTTPretty.GET,
        re.compile(r"https://api.yipit.com:1234/v1/deal;brand=(?P<brand_name>\w+)"),
        body=lambda method, uri, headers: [200, headers, uri]
    )

    response = requests.get('https://api.yipit.com:1234/v1/deal;brand=gap?first_name=chuck&last_name=norris')

    assert response.text=='https://api.yipit.com:1234/v1/deal;brand=gap?first_name=chuck&last_name=norris'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='/v1/deal;brand=gap?first_name=chuck&last_name=norris'


@pytest.mark.skip(reason="hangs indefinietly on requests.get")
@httprettified
def test_httpretty_should_handle_paths_starting_with_two_slashes():
    "HTTPretty should handle URLs with paths starting with //"

    HTTPretty.register_uri(
        HTTPretty.GET, "http://example.com//foo",
        body="Find the best foo"
    )
    response = requests.get('http://example.com//foo')
    assert response.text=='Find the best foo'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path=='//foo'
