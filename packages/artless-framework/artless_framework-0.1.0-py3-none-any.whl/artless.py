"""Artless and minimalistic web framework without dependencies, working over WSGI."""

__author__ = "Peter Bro"
__version__ = "0.1.0"
__license__ = "MIT"
__all__ = ["Request", "Response", "ResponseFactory", "App"]

import logging
import logging.config
from datetime import datetime
from http import HTTPStatus
from re import Pattern, compile, match
from time import time
from traceback import format_exc
from typing import (
    Any,
    Callable,
    ClassVar,
    Mapping,
    MutableMapping,
    Optional,
    ParamSpec,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)
from urllib.parse import parse_qs, quote
from uuid import UUID, uuid4

# Prioritized import of josn library: orjson || ujson || cjson || json (standart module)
try:
    from orjson import JSONEncoder, loads
except ImportError:
    try:
        from json import JSONEncoder

        from ujson import loads
    except ImportError:
        try:
            from cjson import JSONEncoder, loads
        except ImportError:
            from json import JSONEncoder, loads

T = TypeVar("T")
P = ParamSpec("P")
Environ = Mapping[str, Any]
WSGIRetval = TypeVar("WSGIRetval", covariant=True)
CommonData = Mapping | Sequence[T] | str | int | float | bool | datetime | None
StartResponse = Callable[[str, Sequence[tuple[str, str]]], str]

DEFAULT_CONFIG: dict[str, Any] = {
    "DEBUG": False,
    "TEMPLATES_DIR": "templates",
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[{asctime}] [{process:d}] [{levelname}] {message}",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{",
            },
        },
        "handlers": {
            "stdout": {
                "formatter": "default",
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "artless": {
                "level": "DEBUG",
                "handlers": ["stdout"],
                "propagate": False,
            }
        },
        "root": {"level": "WARNING", "handlers": ["stdout"]},
    },
}


def encode_json(data: CommonData, encoder: Type[JSONEncoder] = JSONEncoder) -> str:
    """Encode data to json string."""
    return encoder().encode(data)


@runtime_checkable
class BodyDecoder(Protocol):
    """Protocol, describes interface for response body decoders."""

    def decode(self, body: bytes) -> Mapping[str, CommonData]:
        """Decode body of response."""
        pass


@runtime_checkable
class WSGIProtocol(Protocol[WSGIRetval]):
    """Protocol, describes interface for WSGI applications."""

    def __call__(self, environ: Environ, start_response: StartResponse) -> Sequence[bytes]:
        """Start processing of WSGI-request."""
        pass


class WSGIHeadersParser:
    """Logic of parsing HTTP headers from WSGI request."""

    __slots__ = ("headers", "__weakref__")

    HTTP_PREFIX = "HTTP_"
    UNPREFIXED_HEADERS = {"CONTENT_TYPE", "CONTENT_LENGTH"}

    def __init__(self, environ: Environ) -> None:
        """Initialize a parser object.

        Args:
            environ: WSGI-environ object.
        """
        self.headers: Mapping[str, str] = {}

        for header, value in environ.items():
            if name := self._transcribe_header_name(header):
                self.headers[name] = value

    def _transcribe_header_name(self, header: str) -> Optional[str]:
        """Transcribe WSGI header name to HTTP header name.

        Args:
            header: Native WSGI header (with HTTP_-prefix).

        Returns:
            The native HTTP header name (without HTTP_-prefix).
        """
        if header.startswith(self.HTTP_PREFIX):
            header = header[len(self.HTTP_PREFIX) :]
        elif header not in self.UNPREFIXED_HEADERS:
            return None
        return header.replace("_", "-").title()


class JSONBodyDecoder(BodyDecoder):
    """Decoder for requests with json string in the body."""

    def decode(self, body: bytes) -> Mapping[str, CommonData]:
        """Decode json string from request body."""
        return loads(body)


class WWWFormBodyDecoder(BodyDecoder):
    """Decoder for requests with query string in the body."""

    def decode(self, body: bytes) -> Mapping[str, CommonData]:
        """Decode query string from request body."""
        result = {}
        for param, value in parse_qs(body.decode()).items():
            result[param] = value if len(value) > 1 else value[0]
        return result


class Request:
    """An HTTP request.

    Describes the main attributes of a typical HTTP request, such as:
    method, path, query, headers and body.

    Performs automatic data conversion for json and x-www-form-urlencoded requests.
    """

    __slots__ = (
        "method",
        "path",
        "query_string",
        "query",
        "full_path",
        "headers",
        "body",
        "_id",
        "_raw_body",
        "__weakref__",
    )

    def __init__(self, environ: Environ) -> None:
        """Initialize a Request object.

        Args:
            environ: WSGI-environ object (https://wsgi.readthedocs.io/en/latest/definitions.html).
        """
        self._id = uuid4()

        script_url: str = environ.get("SCRIPT_URL", "").rstrip("/")
        path_info: str = environ.get("PATH_INFO", "/").replace("/", "", 1)
        content_length: int = int(environ.get("CONTENT_LENGTH") or "0")

        self.method: str = environ["REQUEST_METHOD"].upper()
        self.path: str = f"{script_url}/{path_info}"
        self.query_string = environ.get("QUERY_STRING")

        self.query: Mapping[str, Sequence[str]] = {}
        self.full_path: str = self.path

        if self.query_string:
            self.query = parse_qs(self.query_string)
            self.full_path += f"?{self.query_string}"

        self.headers: Mapping[str, str] = WSGIHeadersParser(environ).headers

        self._raw_body: bytes = environ["wsgi.input"].read(content_length)
        self.body: Mapping[str, CommonData] | bytes = self._raw_body
        if decoder := self._get_body_decoder(self.headers["Content-Type"].split(";")[0]):
            self.body = decoder().decode(self._raw_body)

    @property
    def id(self) -> UUID:
        """Property for getting a unique request id."""
        return self._id

    @staticmethod
    def _get_body_decoder(content_type: str) -> Optional[Type[BodyDecoder]]:
        """Get body decoder by content type."""
        available_ctype_decoders = {
            "application/json": JSONBodyDecoder,
            "application/x-www-form-urlencoded": WWWFormBodyDecoder,
        }

        if content_type in available_ctype_decoders:
            return available_ctype_decoders[content_type]

        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}, {self.method}, '{self.full_path}'>"


class Response:
    """An HTTP response.

    Provides the ability to construct a response by specifying the status, headers and body.
    """

    __slots__ = ("_headers", "_body", "_status", "__weakref__")

    CTYPE_HEADER_NAME: ClassVar[str] = "Content-Type"
    DEFAULT_CTYPE: ClassVar[str] = "text/plain"

    def __init__(self, *, status: HTTPStatus = HTTPStatus.OK) -> None:
        """Initialize a Response object.

        Args:
            status: custom http status (code and reason). By default is "200 OK".
        """
        self._headers: MutableMapping[str, str] = {
            Response.CTYPE_HEADER_NAME: Response.DEFAULT_CTYPE
        }
        self._body: bytes = b""
        self._status: HTTPStatus = status

    @property
    def headers(self) -> Sequence[tuple[str, str]]:
        """Get response headers collection."""
        return [(name, value) for name, value in self._headers.items()]

    @property
    def status(self) -> str:
        """Get response status."""
        return f"{self._status.value} {self._status.phrase}"

    @status.setter
    def status(self, status: HTTPStatus) -> None:
        """Set response status."""
        self._status = status

    @property
    def content_type(self) -> str:
        """Get content_type response header value."""
        return self._headers[Response.CTYPE_HEADER_NAME]

    @content_type.setter
    def content_type(self, value: str):
        """Set content_type response header value."""
        self._headers[Response.CTYPE_HEADER_NAME] = value

    @property
    def body(self) -> Sequence[bytes]:
        """Get response body."""
        return [self._body]

    @body.setter
    def body(self, data: Union[str, bytes]) -> None:
        """Set response body."""
        if isinstance(data, str):
            self._body = (data + "\n").encode("utf-8")
        elif isinstance(data, bytes):
            data += b"\n"
            self._body = data
        else:
            raise TypeError(f"Response body must be only string or bytes, not {type(data)}")
        self._headers["Content-Length"] = str(len(self._body))


class ResponseFactory:
    """Factory to easily create concrete response objects."""

    __slots__: set[str] = set()

    @classmethod
    def create(cls: Type["ResponseFactory"], /, *, status: HTTPStatus = HTTPStatus.OK) -> Response:
        """Create a blank Response object."""
        response = Response()
        response.status = status  # type: ignore[assignment]
        return response

    @classmethod
    def plain(
        cls: Type["ResponseFactory"], message: str, /, *, status: HTTPStatus = HTTPStatus.OK
    ) -> Response:
        """Create Response object with an plain text in the body."""
        response = Response(status=status)
        response.body = message  # type: ignore[assignment]
        return response

    @classmethod
    def html(
        cls: Type["ResponseFactory"], template: str, /, *, status: HTTPStatus = HTTPStatus.OK
    ) -> Response:
        """Create Response object with an HTML document in the body."""
        response = Response(status=status)
        response.content_type = "text/html"
        response.body = template  # type: ignore[assignment]
        return response

    @classmethod
    def json(
        cls: Type["ResponseFactory"], data: CommonData, /, *, status: HTTPStatus = HTTPStatus.OK
    ) -> Response:
        """Create Response object with an JSON document in the body."""
        response = Response(status=status)
        response.content_type = "application/json"
        response.body = encode_json(data)  # type: ignore[assignment]
        return response

    @classmethod
    def redirect(
        cls: Type["ResponseFactory"],
        redirect_url: str,
        /,
        *,
        status: HTTPStatus = HTTPStatus.MOVED_PERMANENTLY,
    ) -> Response:
        """Create Response object for redirect."""
        response = Response(status=status)
        response._headers["Location"] = quote(redirect_url)
        return response


class App(WSGIProtocol):
    """WSGI application."""

    __slots__ = ("config", "_start_response", "_routing_table", "_id", "_start_time", "_logger")

    def __init__(self, config: Optional[dict[str, CommonData]] = None) -> None:
        """Initialize an WSGI application object.

        Args:
            config: The dictionary with settings/constants.
        """
        self.config = DEFAULT_CONFIG | config if config else DEFAULT_CONFIG
        self._routing_table: MutableMapping[
            str, MutableMapping[Pattern, Callable[[Request], Response]]
        ] = {}

        logging.config.dictConfig(self.config["LOGGING"])
        self._logger = logging.getLogger(__name__)

    def __call__(self, environ: Environ, start_response: StartResponse):
        """WSGI handler of request."""
        self._start_time = time()
        self._start_response = start_response

        request = Request(environ)

        method, path = (request.method, request.path)

        if method not in self._routing_table:
            return self._wsgi_response(request, Response(status=HTTPStatus.METHOD_NOT_ALLOWED))

        handler, params = self._get_request_handler(method, path)

        if not handler:
            return self._wsgi_response(request, Response(status=HTTPStatus.NOT_FOUND))

        try:
            response = handler(request, **params)
        except Exception:
            response = Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
            stack_trace = format_exc()

            if self.config["DEBUG"]:
                response.body = stack_trace  # type: ignore[assignment]

            self._logger.error(f"[{request.id}] {stack_trace}")

        return self._wsgi_response(request, response)

    def set_routes(self, routes: Sequence[tuple[str, str, Callable]]) -> None:
        """Set the routes table."""
        for route in routes:
            self._add_route(*route)

    def _wsgi_response(self, request: Request, response: Response) -> Sequence[bytes]:
        """Make WSGI response (by WSGI protocol)."""
        deltatime_ms = (time() - self._start_time) * 1000

        self._logger.info(
            f'[{request.id}] "{request.method} {request.path}" '
            f"{response.status} in {deltatime_ms:.3f}ms."
        )

        self._start_response(response.status, response.headers)
        return response.body

    def _add_route(self, method: str, path: str, handler: Callable) -> None:
        """Add route to routes table."""
        method = method.upper()
        compiled_re_path = compile(path)

        if method not in self._routing_table:
            self._routing_table[method] = {}

        if compiled_re_path in self._routing_table[method]:
            raise ValueError(f'Route for "{method} {path}" already exists!')

        self._routing_table[method][compiled_re_path] = handler

    def _get_request_handler(
        self, method: str, url_path: str
    ) -> tuple[Callable[[Request], Response] | None, dict[str, str | Any] | None]:
        """Get request handler based on method and URL."""
        for pattern, handler in self._routing_table[method].items():
            if m := match(pattern, url_path):
                return handler, m.groupdict()
        return None, None
