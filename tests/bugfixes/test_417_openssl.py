# This test is based on @ento's example snippet:
# https://gist.github.com/ento/e1e33d7d67e406bf03fe61f018404c21

# Original Issue:
# https://github.com/gabrielfalcao/HTTPretty/issues/417
import httpretty
import urllib3
import pytest
try:
    from urllib3.contrib.pyopenssl import extract_from_urllib3
except Exception:
    extract_from_urllib3 = None


@pytest.mark.skipif(extract_from_urllib3 is None,
        reason="urllib3.contrib.pyopenssl.extract_from_urllib3 does not exist")
def test_enable_disable_httpretty_extract():
    # TODO: This is a very incorrect test, and must be revaluated
    "#417 urllib3.contrib.pyopenssl enable -> disable extract"
    extract_from_urllib3()
    assert urllib3.util.IS_PYOPENSSL is False
    httpretty.enable()
    httpretty.disable()
    extract_from_urllib3()
    assert urllib3.util.IS_PYOPENSSL is False
