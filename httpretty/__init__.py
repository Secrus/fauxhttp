# #!/usr/bin/env python
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
from __future__ import annotations

from httpretty.core import EmptyRequestHeaders
from httpretty.core import Entry
from httpretty.core import HTTPrettyRequest
from httpretty.core import HTTPrettyRequestEmpty
from httpretty.core import URIInfo
from httpretty.core import URIMatcher
from httpretty.core import get_default_thread_timeout
from httpretty.core import httprettified
from httpretty.core import httprettized
from httpretty.core import httpretty
from httpretty.core import set_default_thread_timeout
from httpretty.errors import HTTPrettyError
from httpretty.errors import UnmockedError


HTTPretty = httpretty
activate = httprettified

enabled = httprettized

enable = httpretty.enable
register_uri = httpretty.register_uri
disable = httpretty.disable
is_enabled = httpretty.is_enabled
reset = httpretty.reset
Response = httpretty.Response

GET = httpretty.GET
"""Match requests of GET method"""
PUT = httpretty.PUT
"""Match requests of PUT method"""
POST = httpretty.POST
"""Match requests of POST method"""
DELETE = httpretty.DELETE
"""Match requests of DELETE method"""
HEAD = httpretty.HEAD
"""Match requests of HEAD method"""
PATCH = httpretty.PATCH
"""Match requests of OPTIONS method"""
OPTIONS = httpretty.OPTIONS
"""Match requests of OPTIONS method"""
CONNECT = httpretty.CONNECT
"""Match requests of CONNECT method"""


def last_request():
    """
    :returns: the last :py:class:`~httpretty.core.HTTPrettyRequest`
    """
    return httpretty.last_request


def latest_requests():
    """returns the history of made requests"""
    return httpretty.latest_requests


def has_request():
    """
    :returns: bool - whether any request has been made
    """
    return not isinstance(httpretty.last_request.headers, EmptyRequestHeaders)


__all__ = [
    "GET",
    "PUT",
    "DELETE",
    "HEAD",
    "PATCH",
    "POST",
    "OPTIONS",
    "CONNECT",
    "last_request",
    "latest_requests",
    "has_request",
    "HTTPretty",
    "HTTPrettyRequestEmpty",
    "HTTPrettyRequest",
    "enable",
    "activate",
    "disable",
    "HTTPretty",
    "activate",
    "enabled",
    "enable",
    "register_uri",
    "disable",
    "is_enabled",
    "reset",
    "Response",
    "UnmockedError",
    "HTTPrettyError",
    "set_default_thread_timeout",
    "URIMatcher",
    "URIInfo",
    "Entry",
    "get_default_thread_timeout",
]
