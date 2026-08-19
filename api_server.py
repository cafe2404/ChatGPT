from typing import Any
from urllib.parse import ParseResult, urlparse
from pydantic import BaseModel, Field
from wrapper import ChatGPT


def cookie_string_to_dict(cookie_string: str) -> dict[str, str]:
    """Convert a browser Cookie header string to a cookie dictionary."""
    result: dict[str, str] = {}

    for item in cookie_string.split(";"):
        item = item.strip()
        if not item or "=" not in item:
            continue

        name, value = item.split("=", 1)
        name = name.strip()
        value = value.strip()

        if name:
            result[name] = value

    return result


def normalize_cookies(
    cookie_string: str | None = None,
    cookies: dict[str, str] | None = None,
) -> dict[str, str] | None:
    """Normalize either cookies or cookie_string to one internal format.

    If both are supplied, the explicit cookies dictionary takes precedence.
    """
    if cookies:
        return {str(key): str(value) for key, value in cookies.items()}

    if cookie_string:
        parsed = cookie_string_to_dict(cookie_string)
        return parsed or None

    return None


def format_proxy(proxy: str) -> str:
    if not proxy.startswith(("http://", "https://")):
        proxy = "http://" + proxy

    try:
        parsed: ParseResult = urlparse(proxy)

        if parsed.scheme not in ("http", "https"):
            raise ValueError("Not http/https scheme")

        if not parsed.hostname or not parsed.port:
            raise ValueError("No host and port")

        if parsed.username and parsed.password:
            return (
                f"{parsed.scheme}://{parsed.username}:{parsed.password}"
                f"@{parsed.hostname}:{parsed.port}"
            )

        return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid proxy format: {str(exc)}",
        ) from exc
