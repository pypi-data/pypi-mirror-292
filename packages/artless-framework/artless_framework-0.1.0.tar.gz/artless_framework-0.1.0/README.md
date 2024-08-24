# artless-framework

<!-- ![Build Status](https://github.com/p3t3rbr0/py3-artless-framework/actions/workflows/ci.yaml/badge.svg?branch=master) -->
[![Downloads](https://static.pepy.tech/badge/artless-framework)](https://pepy.tech/project/artless-framework)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/artless-framework)
![PyPI Version](https://img.shields.io/pypi/v/artless-framework)
<!-- [![Code Coverage](https://codecov.io/gh/p3t3rbr0/py3-artless-framework/graph/badge.svg?token=N7J33ZOKVO)](https://codecov.io/gh/p3t3rbr0/py3-artless-framework) -->
<!-- [![Maintainability](https://api.codeclimate.com/v1/badges/76cc047808f3dc53de01/maintainability)](https://codeclimate.com/github/p3t3rbr0/py3-artless-framework/maintainability) -->

The artless and minimalistic web framework without dependencies, working over WSGI.

## Main principles

1. Artless, fast and small (less then 1000 LOC) WSGI-framework.
2. No third party dependencies (standart library only).
3. Support only modern versions of Python (>=3.10).
4. Integrated with most popular WSGI-servers.
5. Mostly pure functions without side effects.
6. Interfaces with type annotations.
7. Comprehensive documentation with examples of use.
8. Full test coverage.

## Limitations

* No built-in support for working with `Cookies`.
* Requests with `multipart/form-data` content-type are not supported.
* No built-in protections, such as: CSRF, XSS, clickjacking and other attack techniques.

## Usages

``` python
from os import getenv

from artless import App, Request, Response, ResponseFactory


def say_hello(request: Request, username: str) -> Response:
    return ResponseFactory.plain(f"Hello, {username}!")


def create_application(config) -> App:
    app = App(config)
    app.set_routes((("GET", r"^/hello/(?P<username>\w+)/$", say_hello),))
    return app


config = {
    "DEBUG": True,
}

application = create_application(config)

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
$ curl http://127.0.0.1:8000/hello/Peter/
Hello, Peter!
```

See more [examples](https://git.peterbro.su/peter/py3-artless-framework/src/branch/master/examples).

## Roadmap

- [ ] Add plugin support.
- [ ] Add cookies support.
- [ ] Add async interface.
- [ ] Add `multipart/form-data` support.
- [ ] Add test client.
- [ ] Add benchmarks.
- [ ] Add more examples.
