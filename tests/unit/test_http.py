from httpretty.http import parse_requestline


def test_parse_request_line_connect():
    """parse_requestline should parse the CONNECT method appropriately"""
    assert parse_requestline("CONNECT / HTTP/1.1") == ("CONNECT", "/", "1.1")
