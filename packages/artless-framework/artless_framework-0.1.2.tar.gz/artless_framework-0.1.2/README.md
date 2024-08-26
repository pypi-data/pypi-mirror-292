# artless-framework

<!-- ![Build Status](https://github.com/p3t3rbr0/py3-artless-framework/actions/workflows/ci.yaml/badge.svg?branch=master) -->
[![Downloads](https://static.pepy.tech/badge/artless-framework)](https://pepy.tech/project/artless-framework)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/artless-framework)
![PyPI Version](https://img.shields.io/pypi/v/artless-framework)
<!-- [![Code Coverage](https://codecov.io/gh/p3t3rbr0/py3-artless-framework/graph/badge.svg?token=N7J33ZOKVO)](https://codecov.io/gh/p3t3rbr0/py3-artless-framework) -->
<!-- [![Maintainability](https://api.codeclimate.com/v1/badges/76cc047808f3dc53de01/maintainability)](https://codeclimate.com/github/p3t3rbr0/py3-artless-framework/maintainability) -->

The artless and minimalistic web framework without dependencies, working over WSGI.

## Main principles

1. Artless, fast and small (less then 1000 LOC into single file) WSGI-framework.
2. No third party dependencies (standart library only).
3. Support only modern versions of Python (>=3.10).
4. Mostly pure functions without side effects.
5. Interfaces with type annotations.
6. Comprehensive documentation with examples of use.
7. Full test coverage.

## Limitations

* No built-in support for working with `Cookies`.
* Requests with `multipart/form-data` content-type are not supported.
* No built-in protections, such as: CSRF, XSS, clickjacking and other attack techniques.

## Installation

``` shellsession
$ pip install artless-framework
```

## Usages

``` python
from http import HTTPStatus
from os import getenv
from string import Template

from artless import App, Request, Response, ResponseFactory

HTML_TEMPLATE = Template(
    """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Say hello</title>
      </head>
      <body>
        <h1>Hello, $username!</h1>
      </body>
    </html>
    """
)


def say_hello(request: Request, username: str) -> Response:
    available_formats = {
        "json": ResponseFactory.json({"hello": username}),
        "plain": ResponseFactory.plain(f"Hello, {username}!"),
        "html": ResponseFactory.html(HTML_TEMPLATE.substitute(username=username)),
    }

    format = request.query.get("format", ["plain"])[0]

    if format not in available_formats:
        return ResponseFactory.create(status=HTTPStatus.BAD_REQUEST)

    return available_formats[format]


def create_application() -> App:
    app = App()
    app.set_routes([("GET", r"^/hello/(?P<username>\w+)$", say_hello)])
    return app


application = create_application()

if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    host = getenv("HOST", "127.0.0.1")
    port = int(getenv("PORT", 8000))

    with make_server(host, port, application) as httpd:
        print(f"Started WSGI server on {host}:{port}")
        httpd.serve_forever()
```

Run it:

``` shellsession
$ python3 app.py
Started WSGI server on 127.0.0.1:8000
```

Check it:

``` shellsession
$ curl http://127.0.0.1:8000/hello/Peter
Hello, Peter!

$ curl http://127.0.0.1:8000/hello/Peter?format=html

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Say hello</title>
  </head>
  <body>
    <h1>Hello, Peter!</h1>
  </body>
</html>

$ curl http://127.0.0.1:8000/hello/Peter?format=json
{"hello": "Peter"}
```

See more [examples](https://git.peterbro.su/peter/py3-artless-framework/src/branch/master/examples).

## Configureation

By default, the application defines the following config:

``` python
{
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
                "level": "INFO",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "artless": {
                "level": "INFO",
                "handlers": ["stdout"],
                "propagate": False,
            }
        },
        "root": {"level": "WARNING", "handlers": ["stdout"]},
    },
}
```

Before creating an application instance, set the configuration by overriding existing values ​​and/or adding a new ones:

``` python
from artless import Config, App


Config().replace({"debug": True, "database": {"host": "localhost"}})
application = App()
```

To get values ​​from the config, anywhere in the application:

``` python
from artless import Config


db_host = Config().database.get("host")
...
```

## Roadmap

- [ ] Add plugin support.
- [ ] Add cookies support.
- [ ] Add async interface.
- [ ] Add `multipart/form-data` support.
- [ ] Add test client.
- [ ] Add benchmarks.
- [ ] Add more examples.
