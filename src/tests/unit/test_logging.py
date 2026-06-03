import logging

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from src.main import (
    REDACTED_EMAIL,
    global_exception_handler,
    log_http_exception,
    sentry_before_send,
)


@pytest.mark.asyncio
async def test_http_exception_logs_detail(caplog):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/resource-server/groups/",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "scheme": "http",
            "client": ("testclient", 50000),
        }
    )
    exception = HTTPException(
        status_code=401,
        detail="Token does not contain 'sub' claim",
        headers={"WWW-Authenticate": "Bearer"},
    )

    with caplog.at_level(logging.ERROR, logger="src"):
        response = await log_http_exception(request, exception)

    assert response.status_code == 401
    assert "HTTPException 401 on GET /resource-server/groups/" in caplog.text
    assert "Token does not contain 'sub' claim" in caplog.text


@pytest.mark.asyncio
async def test_http_exception_anonymizes_email_in_logs_and_sentry(
    caplog, monkeypatch
):
    captured_exceptions = []
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/resource-server/groups/",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "scheme": "http",
            "client": ("testclient", 50000),
        }
    )
    exception = HTTPException(
        status_code=403,
        detail="User alice@example.com cannot access this resource",
    )

    def fake_capture_exception(exception):
        captured_exceptions.append(exception)

    monkeypatch.setattr("src.main.sentry_sdk.capture_exception", fake_capture_exception)

    with caplog.at_level(logging.ERROR, logger="src"):
        response = await log_http_exception(request, exception)

    assert response.status_code == 403
    assert "alice@example.com" not in caplog.text
    assert f"User {REDACTED_EMAIL} cannot access this resource" in caplog.text
    assert captured_exceptions[0].detail == (
        f"User {REDACTED_EMAIL} cannot access this resource"
    )


def test_sentry_before_send_anonymizes_nested_email_values():
    event = {
        "message": "Failure for alice@example.com",
        "exception": {
            "values": [
                {
                    "value": "bob@example.org cannot access alice@example.com data",
                }
            ]
        },
    }

    anonymized_event = sentry_before_send(event, {})

    assert "alice@example.com" not in str(anonymized_event)
    assert "bob@example.org" not in str(anonymized_event)
    assert REDACTED_EMAIL in anonymized_event["message"]


@pytest.mark.asyncio
async def test_unexpected_exception_anonymizes_email_in_logs(caplog, monkeypatch):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/resource-server/groups/",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "scheme": "http",
            "client": ("testclient", 50000),
        }
    )
    exception = RuntimeError("Could not load alice@example.com")

    monkeypatch.setattr("src.main.sentry_sdk.capture_exception", lambda _: None)

    with caplog.at_level(logging.ERROR, logger="src"):
        response = await global_exception_handler(request, exception)

    assert response.status_code == 500
    assert "alice@example.com" not in caplog.text
    assert f"Could not load {REDACTED_EMAIL}" in caplog.text
