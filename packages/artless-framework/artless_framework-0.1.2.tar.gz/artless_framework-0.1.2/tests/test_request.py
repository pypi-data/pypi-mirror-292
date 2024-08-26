from io import BytesIO
from json import dumps
from typing import Any
from unittest import TestCase
from uuid import UUID

from artless import Request


def create_environ(data) -> dict[str, Any]:
    wsgi_input_data = data.get("wsgi.input", b"")
    content_length = len(wsgi_input_data)

    wsgi_input = BytesIO()
    wsgi_input.write(wsgi_input_data)
    wsgi_input.seek(0)

    environ = {
        "SCRIPT_URL": data.get("SCRIPT_URL", "/"),
        "PATH_INFO": data.get("PATH_INFO", "/some/test/url"),
        "CONTENT_LENGTH": content_length,
        "REQUEST_METHOD": data.get("REQUEST_METHOD", "GET"),
        "QUERY_STRING": data.get("QUERY_STRING", ""),
        "HTTP_HOST": data.get("HTTP_HOST", "test.com"),
        "HTTP_USER_AGENT": data.get("HTTP_USER_AGENT", "test ua"),
        "wsgi.input": wsgi_input,
    }

    environ |= {k: v for k, v in data.items() if k.startswith("HTTP_")}

    return environ


class TestRequest(TestCase):
    def test_attributes(self):
        wsgi_input = b"some data"
        environ = create_environ(
            {
                "QUERY_STRING": "a=10&b=test",
                "HTTP_CONTENT_TYPE": "text/html; charset=utf-8",
                "wsgi.input": wsgi_input,
            }
        )

        request = Request(environ)

        self.assertTrue(request.id, UUID)
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.path, "/some/test/url")
        self.assertEqual(request.full_path, "/some/test/url?a=10&b=test")
        self.assertEqual(request.query_string, "a=10&b=test")
        self.assertEqual(request.query, {"a": ["10"], "b": ["test"]})
        self.assertEqual(
            request.headers,
            {
                "Content-Length": len(wsgi_input),
                "Content-Type": "text/html; charset=utf-8",
                "Host": "test.com",
                "User-Agent": "test ua",
            },
        )
        self.assertEqual(request.body, b"some data")
        self.assertEqual(repr(request), "<Request, GET, '/some/test/url?a=10&b=test'>")

    def test_request_with_json(self):
        environ = create_environ(
            {
                "HTTP_CONTENT_TYPE": "application/json",
                "wsgi.input": dumps({"some": {"data": True}}).encode(),
            }
        )

        request = Request(environ)

        self.assertEqual(request.headers["Content-Type"], "application/json")
        self.assertEqual(request.body, {"some": {"data": True}})

    def test_request_with_www_form_urlencoded(self):
        environ = create_environ(
            {
                "HTTP_CONTENT_TYPE": "application/x-www-form-urlencoded",
                "wsgi.input": b"a=10&b=test",
            }
        )

        request = Request(environ)

        self.assertEqual(request.headers["Content-Type"], "application/x-www-form-urlencoded")
        self.assertEqual(request.body, {"a": "10", "b": "test"})
