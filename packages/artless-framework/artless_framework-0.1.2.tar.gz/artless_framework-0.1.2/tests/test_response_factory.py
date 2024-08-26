from http import HTTPStatus
from unittest import TestCase

from artless import Response, ResponseFactory


class TestResponseFactory(TestCase):
    def test_create(self):
        # Create common response with default status
        response = ResponseFactory.create()
        self.assertTrue(response)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(response.body, [b""])

        # Create common response with custom status
        response = ResponseFactory.create(status=HTTPStatus.NO_CONTENT)
        self.assertEqual(response.status, "204 No Content")

    def test_plain(self):
        response = ResponseFactory.plain("some response message")
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(response.body, [b"some response message\n"])

    def test_html(self):
        response = ResponseFactory.html(
            "<html><head><title>Title</title></head><body><h1>Hello!</h1></body></html>"
        )
        self.assertEqual(response.content_type, "text/html")
        self.assertEqual(
            response.body,
            [b"<html><head><title>Title</title></head><body><h1>Hello!</h1></body></html>\n"],
        )

    def test_json(self):
        response = ResponseFactory.json([{"some": {"native": ["structure"]}}])
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.body, [b'[{"some": {"native": ["structure"]}}]\n'])

    def test_redirect(self):
        response = ResponseFactory.redirect("/redirect/to/some/url/")
        self.assertEqual(response.content_type, "text/plain")
        self.assertEqual(
            response.headers,
            [("Content-Type", "text/plain"), ("Location", "/redirect/to/some/url/")],
        )
        self.assertEqual(response.body, [b""])
