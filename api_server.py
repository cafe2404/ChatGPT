from typing import Any
from urllib.parse import ParseResult, urlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uvicorn import run

from wrapper import ChatGPT


app = FastAPI()


class ConversationRequest(BaseModel):
    proxy: str | None = None
    message: str
    image: str | None = None
    cookie_string: str | None = None
    cookies: dict[str, str] | None = Field(default=None)


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


@app.post("/conversation")
async def create_conversation(request: ConversationRequest) -> dict[str, Any]:
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")

    proxy = format_proxy(request.proxy) if request.proxy else None
    cookies = normalize_cookies(request.cookie_string, request.cookies)

    try:
        client = ChatGPT(proxy=proxy, cookies=cookies)

        if request.image:
            answer = client.ask_question(request.message, request.image)
        else:
            answer = client.ask_question(request.message)

        return {
            "status": "success",
            "result": answer,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=6969)
