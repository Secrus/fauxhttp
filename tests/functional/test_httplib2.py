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
from __future__ import unicode_literals

import re
import httplib2
from freezegun import freeze_time
from httpretty import HTTPretty, httprettified
from httpretty.core import decode_utf8


@httprettified
#@within(two=miliseconds)
def test_httpretty_should_mock_a_simple_get_with_httplib2_read():
    "HTTPretty should mock a simple GET with httplib2.context.http"

    HTTPretty.register_uri(HTTPretty.GET, "http://yipit.com/",
                           body="Find the best daily deals")

    _, got = httplib2.Http().request('http://yipit.com', 'GET')
    assert got == b'Find the best daily deals'

    assert HTTPretty.last_request.method == 'GET'
    assert HTTPretty.last_request.path == '/'


@httprettified
#@within(two=miliseconds)
def test_httpretty_provides_easy_access_to_querystrings():
    "HTTPretty should provide an easy access to the querystring"

    HTTPretty.register_uri(HTTPretty.GET, "http://yipit.com/",
                           body="Find the best daily deals")

    httplib2.Http().request('http://yipit.com?foo=bar&foo=baz&chuck=norris', 'GET')
    assert HTTPretty.last_request.querystring == {
        'foo': ['bar', 'baz'],
        'chuck': ['norris'],
    }


@httprettified
@freeze_time("2013-10-04 04:20:00")
def test_httpretty_should_mock_headers_httplib2():
    "HTTPretty should mock basic headers with httplib2"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/",
                           body="this is supposed to be the response",
                           status=201)

    headers, _ = httplib2.Http().request('http://github.com', 'GET')
    assert headers['status'] == '201'
    assert dict(headers) == {
        'content-type': 'text/plain; charset=utf-8',
        'connection': 'close',
        'content-length': '35',
        'status': '201',
        'server': 'Python/HTTPretty',
        'date': 'Fri, 04 Oct 2013 04:20:00 GMT',
    }


@httprettified
@freeze_time("2013-10-04 04:20:00")
def test_httpretty_should_allow_adding_and_overwritting_httplib2():
    "HTTPretty should allow adding and overwritting headers with httplib2"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/foo",
                           body="this is supposed to be the response",
                           adding_headers={
                               'Server': 'Apache',
                               'Content-Length': '27',
                               'Content-Type': 'application/json',
                           })

    headers, _ = httplib2.Http().request('http://github.com/foo', 'GET')

    assert dict(headers) == {
        'content-type': 'application/json',
        'content-location': 'http://github.com/foo',
        'connection': 'close',
        'content-length': '27',
        'status': '200',
        'server': 'Apache',
        'date': 'Fri, 04 Oct 2013 04:20:00 GMT',
    }


@httprettified
#@within(two=miliseconds)
def test_httpretty_should_allow_forcing_headers_httplib2():
    "HTTPretty should allow forcing headers with httplib2"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/foo",
                           body="this is supposed to be the response",
                           forcing_headers={
                               'Content-Type': 'application/xml',
                           })

    headers, _ = httplib2.Http().request('http://github.com/foo', 'GET')

    assert dict(headers) == {
        'content-location': 'http://github.com/foo',  # httplib2 FORCES
                                                      # content-location
                                                      # even if the
                                                      # server does not
                                                      # provide it
        'content-type': 'application/xml',
        'status': '200',  # httplib2 also ALWAYS put status on headers
    }


@httprettified
@freeze_time("2013-10-04 04:20:00")
def test_httpretty_should_allow_adding_and_overwritting_by_kwargs_u2():
    "HTTPretty should allow adding and overwritting headers by keyword args " \
        "with httplib2"

    HTTPretty.register_uri(HTTPretty.GET, "http://github.com/foo",
                           body="this is supposed to be the response",
                           server='Apache',
                           content_length='27',
                           content_type='application/json')

    headers, _ = httplib2.Http().request('http://github.com/foo', 'GET')

    assert dict(headers) == {
        'content-type': 'application/json',
        'content-location': 'http://github.com/foo',  # httplib2 FORCES
                                                      # content-location
                                                      # even if the
                                                      # server does not
                                                      # provide it
        'connection': 'close',
        'content-length': '27',
        'status': '200',
        'server': 'Apache',
        'date': 'Fri, 04 Oct 2013 04:20:00 GMT',
    }


@httprettified
#@within(two=miliseconds)
def test_rotating_responses_with_httplib2():
    "HTTPretty should support rotating responses with httplib2"

    HTTPretty.register_uri(
        HTTPretty.GET, "https://api.yahoo.com/test",
        responses=[
            HTTPretty.Response(body="first response", status=201),
            HTTPretty.Response(body='second and last response', status=202),
        ])

    headers1, body1 = httplib2.Http().request(
        'https://api.yahoo.com/test', 'GET')

    assert headers1['status'] == '201'
    assert body1 == b'first response'

    headers2, body2 = httplib2.Http().request(
        'https://api.yahoo.com/test', 'GET')

    assert headers2['status'] == '202'
    assert body2 == b'second and last response'

    headers3, body3 = httplib2.Http().request(
        'https://api.yahoo.com/test', 'GET')

    assert headers3['status'] == '202'
    assert body3 == b'second and last response'


@httprettified
#@within(two=miliseconds)
def test_can_inspect_last_request():
    "HTTPretty.last_request is a mimetools.Message request from last match"

    HTTPretty.register_uri(HTTPretty.POST, "http://api.github.com/",
                           body='{"repositories": ["HTTPretty", "lettuce"]}')

    headers, body = httplib2.Http().request(
        'http://api.github.com', 'POST',
        body='{"username": "gabrielfalcao"}',
        headers={
            'content-type': 'text/json',
        },
    )

    assert HTTPretty.last_request.method == 'POST'
    assert HTTPretty.last_request.body == b'{"username": "gabrielfalcao"}'
    assert HTTPretty.last_request.headers['content-type'] == 'text/json'
    assert body == b'{"repositories": ["HTTPretty", "lettuce"]}'


@httprettified
#@within(two=miliseconds)
def test_can_inspect_last_request_with_ssl():
    "HTTPretty.last_request is recorded even when mocking 'https' (SSL)"

    HTTPretty.register_uri(HTTPretty.POST, "https://secure.github.com/",
                           body='{"repositories": ["HTTPretty", "lettuce"]}')

    headers, body = httplib2.Http().request(
        'https://secure.github.com', 'POST',
        body='{"username": "gabrielfalcao"}',
        headers={
            'content-type': 'text/json',
        },
    )

    assert HTTPretty.last_request.method == 'POST'
    assert HTTPretty.last_request.body == b'{"username": "gabrielfalcao"}'
    assert HTTPretty.last_request.headers['content-type'] == 'text/json'
    assert body == b'{"repositories": ["HTTPretty", "lettuce"]}'


@httprettified
#@within(two=miliseconds)
def test_httpretty_ignores_querystrings_from_registered_uri():
    "Registering URIs with query string cause them to be ignored"

    HTTPretty.register_uri(HTTPretty.GET, "http://yipit.com/?id=123",
                           body="Find the best daily deals")

    _, got = httplib2.Http().request('http://yipit.com/?id=123', 'GET')

    assert got == b'Find the best daily deals'
    assert HTTPretty.last_request.method == 'GET'
    assert HTTPretty.last_request.path == '/?id=123'


@httprettified
#@within(two=miliseconds)
def test_callback_response():
    ("HTTPretty should call a callback function to be set as the body with"
     " httplib2")

    def request_callback(request, uri, headers):
        return [200, headers, "The {} response from {}".format(decode_utf8(request.method), uri)]

    HTTPretty.register_uri(
        HTTPretty.GET, "https://api.yahoo.com/test",
        body=request_callback)

    headers1, body1 = httplib2.Http().request(
        'https://api.yahoo.com/test', 'GET')

    assert body1 == b"The GET response from https://api.yahoo.com/test"

    HTTPretty.register_uri(
        HTTPretty.POST, "https://api.yahoo.com/test_post",
        body=request_callback)

    headers2, body2 = httplib2.Http().request(
        'https://api.yahoo.com/test_post', 'POST')

    assert body2 == b"The POST response from https://api.yahoo.com/test_post"


@httprettified
def test_httpretty_should_allow_registering_regexes():
    "HTTPretty should allow registering regexes with httplib2"

    HTTPretty.register_uri(
        HTTPretty.GET,
        'http://api.yipit.com/v1/deal;brand=gap',
        body="Found brand",
    )

    response, body = httplib2.Http().request('http://api.yipit.com/v1/deal;brand=gap', 'GET')
    assert body == b'Found brand'
    assert HTTPretty.last_request.method=='GET'
    assert HTTPretty.last_request.path == '/v1/deal;brand=gap'
