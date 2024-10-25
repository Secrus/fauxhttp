from unittest import TestCase
from httpretty import httprettified, HTTPretty

import urllib.request as urllib2


@httprettified
def test_decor():
    HTTPretty.register_uri(
        HTTPretty.GET, "http://localhost/",
        body="glub glub")

    fd = urllib2.urlopen('http://localhost/')
    got1 = fd.read()
    fd.close()

    assert got1 == b'glub glub'


@httprettified
class DecoratedNonUnitTest(object):

    def test_fail(self):
        raise AssertionError('Tests in this class should not '
                             'be executed by the test runner.')

    def test_decorated(self):
        HTTPretty.register_uri(
            HTTPretty.GET, "http://localhost/",
            body="glub glub")

        fd = urllib2.urlopen('http://localhost/')
        got1 = fd.read()
        fd.close()

        assert got1 == b'glub glub'


class NonUnitTestTest(TestCase):
    """
    Checks that the test methods in DecoratedNonUnitTest were decorated.
    """

    def test_decorated(self):
        DecoratedNonUnitTest().test_decorated()


@httprettified
class ClassDecorator(TestCase):

    def test_decorated(self):
        HTTPretty.register_uri(
            HTTPretty.GET, "http://localhost/",
            body="glub glub")

        fd = urllib2.urlopen('http://localhost/')
        got1 = fd.read()
        fd.close()

        assert got1 == b'glub glub'

    def test_decorated2(self):
        HTTPretty.register_uri(
            HTTPretty.GET, "http://localhost/",
            body="buble buble")

        fd = urllib2.urlopen('http://localhost/')
        got1 = fd.read()
        fd.close()

        assert got1 == b'buble buble'


@httprettified
class ClassDecoratorWithSetUp(TestCase):

    def setUp(self):
        HTTPretty.register_uri(
            HTTPretty.GET, "http://localhost/",
            responses=[
                HTTPretty.Response("glub glub"),
                HTTPretty.Response("buble buble"),
            ])

    def test_decorated(self):

        fd = urllib2.urlopen('http://localhost/')
        got1 = fd.read()
        fd.close()

        assert got1 == b'glub glub'

        fd = urllib2.urlopen('http://localhost/')
        got2 = fd.read()
        fd.close()

        assert got2 == b'buble buble'

    def test_decorated2(self):

        fd = urllib2.urlopen('http://localhost/')
        got1 = fd.read()
        fd.close()

        assert got1 == b'glub glub'

        fd = urllib2.urlopen('http://localhost/')
        got2 = fd.read()
        fd.close()

        assert got2 == b'buble buble'
