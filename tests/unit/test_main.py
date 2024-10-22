import httpretty
from httpretty.core import HTTPrettyRequest

from unittest.mock import patch


@patch('httpretty.httpretty')
def test_last_request(original):
    """httpretty.last_request() should return httpretty.core.last_request"""
    assert httpretty.last_request() == original.last_request


@patch('httpretty.httpretty')
def test_latest_requests(original):
    """httpretty.latest_requests() should return httpretty.core.latest_requests"""
    assert httpretty.latest_requests() == original.latest_requests


def test_has_request():
    """httpretty.has_request() correctly detects whether or not a request has been made"""
    httpretty.reset()
    assert httpretty.has_request() is False
    with patch('httpretty.httpretty.last_request', return_value=HTTPrettyRequest('')):
        assert httpretty.has_request() is True
