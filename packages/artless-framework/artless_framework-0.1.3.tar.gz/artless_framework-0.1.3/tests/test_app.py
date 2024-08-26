from io import BytesIO
from logging import getLogger
from re import compile
from typing import MutableMapping
from unittest import TestCase
from unittest.mock import Mock, patch

from artless import (
    App,
    Config,
    Request,
    Response,
    ResponseFactory,
    WSGIProtocol,
)

logger = getLogger("artless")
config = Config()


def start_response(*args, **kwargs):
    pass


class TestApp(TestCase):
    def tearDown(self):
        config.replace({"debug": False})

    def test_app_protocol(self):
        app = App()

        self.assertTrue(isinstance(app, WSGIProtocol))
        self.assertTrue(callable(app))

    def test_setting_unique_routes(self):
        def sample_handler():
            pass

        app = App()
        app.set_routes(
            [("GET", "/test/url/1/", sample_handler), ("GET", "/test/url/2/", sample_handler)]
        )

        self.assertEqual(
            app._routing_table,
            {
                "GET": {
                    compile(r"/test/url/1/"): sample_handler,
                    compile(r"/test/url/2/"): sample_handler,
                },
            },
        )

    def test_setting_same_routes(self):
        def sample_handler():
            pass

        app = App()
        url = "/test/url/1/"

        with self.assertRaises(ValueError) as exc:
            app.set_routes([("GET", url, sample_handler), ("GET", url, sample_handler)])

        self.assertEqual(str(exc.exception), f'Route for "GET {url}" already exists!')

    def test_regular_calling_wsgi_app(self):
        def ping_handler(request):
            return ResponseFactory.plain("pong")

        environ = {
            "SCRIPT_URL": "",
            "PATH_INFO": "/ping/",
            "CONTENT_LENGTH": 0,
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "",
            "HTTP_HOST": "test.com",
            "HTTP_USER_AGENT": "test ua",
            "HTTP_CONTENT_TYPE": "text/plain; charset=utf-8",
            "wsgi.input": BytesIO(),
        }

        app = App()
        app.set_routes([("GET", "/ping/", ping_handler)])

        with patch.object(logger, "info") as mock_logger:
            response_body = app(environ, start_response)

        self.assertEqual(response_body[0], b"pong\n")
        mock_logger.assert_called_once()

    def test_calling_wsgi_app_with_not_allowed_method(self):
        environ = {
            "SCRIPT_URL": "",
            "PATH_INFO": "/ping/",
            "CONTENT_LENGTH": 0,
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "",
            "HTTP_HOST": "test.com",
            "HTTP_USER_AGENT": "test ua",
            "HTTP_CONTENT_TYPE": "text/plain; charset=utf-8",
            "wsgi.input": BytesIO(),
        }

        def _fake_wsgi_response(request, response):
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.path, "/ping/")
            self.assertEqual(response.status, ("405 Method Not Allowed"))

        app = App()
        app.set_routes([("POST", "/ping/", lambda: None)])
        app._wsgi_response = _fake_wsgi_response

        app(environ, start_response)

    def test_calling_wsgi_app_with_unexpected_url(self):
        environ = {
            "SCRIPT_URL": "",
            "PATH_INFO": "/some/resource/",
            "CONTENT_LENGTH": 0,
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "",
            "HTTP_HOST": "test.com",
            "HTTP_USER_AGENT": "test ua",
            "HTTP_CONTENT_TYPE": "text/plain; charset=utf-8",
            "wsgi.input": BytesIO(),
        }

        def _fake_wsgi_response(request, response):
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.path, "/some/resource/")
            self.assertEqual(response.status, ("404 Not Found"))

        app = App()
        app.set_routes([("GET", "/ping/", lambda: None)])
        app._wsgi_response = _fake_wsgi_response
        app(environ, start_response)

    def test_calling_wsgi_app_internal_server_error(self):
        environ = {
            "SCRIPT_URL": "",
            "PATH_INFO": "/some/resource/",
            "CONTENT_LENGTH": 0,
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "",
            "HTTP_HOST": "test.com",
            "HTTP_USER_AGENT": "test ua",
            "HTTP_CONTENT_TYPE": "text/plain; charset=utf-8",
            "wsgi.input": BytesIO(),
        }

        def _fake_wsgi_response(request, response):
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.path, "/some/resource/")
            self.assertEqual(response.status, ("500 Internal Server Error"))

        def _fake_extract_request_handler_and_params(method, path):
            def _handler(request, **params):
                raise Exception("Some server error")

            return _handler, None

        with self.subTest("DEBUG mode is FALSE"):
            app = App()
            app.set_routes([("GET", "/ping/", lambda: None)])
            app._wsgi_response = _fake_wsgi_response
            app._extract_request_handler_and_params = _fake_extract_request_handler_and_params

            with patch.object(logger, "error") as mock_logger:
                app(environ, start_response)

            mock_logger.assert_called_once()

        with self.subTest("DEBUG mode is TRUE"):
            config.replace({"debug": True})
            app = App()
            app.set_routes([("GET", "/ping/", lambda: None)])
            app._wsgi_response = _fake_wsgi_response
            app._extract_request_handler_and_params = _fake_extract_request_handler_and_params

            with patch.object(logger, "error") as mock_logger:
                app(environ, start_response)

            mock_logger.assert_called_once()
