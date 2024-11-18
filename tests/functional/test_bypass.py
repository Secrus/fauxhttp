# #!/usr/bin/env python
# -*- coding: utf-8 -*-

# <httpretty - HTTP client mock for Python>
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
import time
import pytest

import requests
from dataclasses import dataclass
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

from .testserver import TornadoServer, TCPServer, TCPClient
from .base import get_free_tcp_port

import functools

import httpretty
from httpretty import core, HTTPretty


@pytest.fixture()
def http_server():
    @dataclass
    class HTTPServerContext:
        server: TornadoServer
        port: int


    if httpretty.httpretty._is_enabled:
        allow_net_connect = httpretty.httpretty.allow_net_connect
    else:
        allow_net_connect = True
    httpretty.disable()
    http_port = get_free_tcp_port()
    context = HTTPServerContext(TornadoServer(http_port), http_port)
    context.server.start()
    ready = False
    timeout = 2
    started_at = time.time()
    while not ready:
        httpretty.disable()
        time.sleep(.1)
        try:
            requests.get('http://localhost:{}/'.format(context.port))
            ready = True
        except Exception:
            if time.time() - started_at >= timeout:
                break

    httpretty.enable(allow_net_connect=allow_net_connect)

    yield context

    context.server.stop()
    httpretty.enable()

@pytest.fixture()
def tcp_server():
    @dataclass
    class TCPServerContext:
        server: TCPServer
        port: int
        client: TCPClient

    tcp_port = get_free_tcp_port()
    server = TCPServer(tcp_port)
    client = TCPClient(tcp_port)
    context = TCPServerContext(server, tcp_port, client)
    context.server.start()
    httpretty.enable()

    yield context

    context.server.stop()
    context.client.close()
    httpretty.enable()


@httpretty.activate
def test_httpretty_bypasses_when_disabled(http_server):
    "httpretty should bypass all requests by disabling it"

    httpretty.register_uri(
        httpretty.GET, "http://localhost:{}/go-for-bubbles/".format(http_server.port),
        body="glub glub")

    httpretty.disable()

    fd = urllib2.urlopen('http://localhost:{}/go-for-bubbles/'.format(http_server.port))
    got1 = fd.read()
    fd.close()

    assert got1 == (
        b'. o O 0 O o . o O 0 O o . o O 0 O o . o O 0 O o . o O 0 O o .')

    fd = urllib2.urlopen('http://localhost:{}/come-again/'.format(http_server.port))
    got2 = fd.read()
    fd.close()

    assert got2 == (b'<- HELLO WORLD ->')

    httpretty.enable()

    fd = urllib2.urlopen('http://localhost:{}/go-for-bubbles/'.format(http_server.port))
    got3 = fd.read()
    fd.close()

    assert got3 == (b'glub glub')
    core.POTENTIAL_HTTP_PORTS.remove(http_server.port)


@httpretty.activate(verbose=True)
def test_httpretty_bypasses_a_unregistered_request(http_server):
    "httpretty should bypass a unregistered request by disabling it"

    httpretty.register_uri(
        httpretty.GET, "http://localhost:{}/go-for-bubbles/".format(http_server.port),
        body="glub glub")

    fd = urllib2.urlopen('http://localhost:{}/go-for-bubbles/'.format(http_server.port))
    got1 = fd.read()
    fd.close()

    assert got1 == b'glub glub'

    fd = urllib2.urlopen('http://localhost:{}/come-again/'.format(http_server.port))
    got2 = fd.read()
    fd.close()

    assert got2 == b'<- HELLO WORLD ->'
    core.POTENTIAL_HTTP_PORTS.remove(http_server.port)


@httpretty.activate(verbose=True)
def test_using_httpretty_with_other_tcp_protocols(tcp_server):
    "httpretty should work even when testing code that also use other TCP-based protocols"

    httpretty.register_uri(
        httpretty.GET, "http://falcao.it/foo/",
        body="BAR")

    fd = urllib2.urlopen('http://falcao.it/foo/')
    got1 = fd.read()
    fd.close()

    assert got1 == b'BAR'

    assert tcp_server.client.send("foobar") == b"RECEIVED: foobar"


@httpretty.activate(allow_net_connect=False, verbose=True)
def test_disallow_net_connect_1(http_server):
    """
    When allow_net_connect = False, a request that otherwise
    would have worked results in UnmockedError.
    """
    httpretty.register_uri(httpretty.GET, "http://falcao.it/foo/",
                           body="BAR")

    def foo():
        fd = None
        try:
            fd = urllib2.urlopen('http://localhost:{}/go-for-bubbles/'.format(http_server.port))
        finally:
            if fd:
                fd.close()

    with pytest.raises(httpretty.UnmockedError):
        foo()


@httpretty.activate(allow_net_connect=False)
def test_disallow_net_connect_2():
    """
    When allow_net_connect = False, a request that would have
    failed results in UnmockedError.
    """

    def foo():
        fd = None
        try:
            fd = urllib2.urlopen('http://example.com/nonsense')
        finally:
            if fd:
                fd.close()

    with pytest.raises(httpretty.UnmockedError):
        foo()


@httpretty.activate(allow_net_connect=False)
def test_disallow_net_connect_3():
    "When allow_net_connect = False, mocked requests still work correctly."

    httpretty.register_uri(httpretty.GET, "http://falcao.it/foo/",
                           body="BAR")
    fd = urllib2.urlopen('http://falcao.it/foo/')
    got1 = fd.read()
    fd.close()
    assert got1 == b'BAR'
