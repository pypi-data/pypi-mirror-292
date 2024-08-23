"""Flywheel client errors."""

from httpx import HTTPStatusError as HTTPStatusErrorOrig

__all__ = [
    "ClientError",
    "Conflict",
    "ConnectionError",
    "HTTPStatusError",
    "NotFound",
    "ServerError",
]


class HTTPStatusError(HTTPStatusErrorOrig):
    """The server returned a response with a status code 4xx/5xx."""

    status_code: int

    def __getattr__(self, name: str):
        """Proxy the response and the request attributes for convenience."""
        try:
            return getattr(self.response, name)
        except AttributeError:
            pass
        try:
            return getattr(self.request, name)
        except AttributeError:
            pass
        raise AttributeError(f"{type(self).__name__} has no attribute {name!r}")


class ClientError(HTTPStatusError):
    """The server returned a response with a 4xx status code."""


class NotFound(ClientError):
    """The server returned a response with a 404 status code."""


class Conflict(ClientError):
    """The server returned a response with a 409 status code."""


class ServerError(HTTPStatusError):
    """The server returned a response with a 5xx status code."""


class ValidationError(Exception):
    """Raised when client configuration is not valid."""


def http_error_str(self) -> str:  # pragma: no cover
    """Return the string representation of an HTTPError."""
    request = self.request or self.response.request
    msg = (
        f"{request.method} {self.response.url} - "
        f"{self.response.status_code} {self.response.reason_phrase}"
    )
    return msg
