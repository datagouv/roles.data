import logging

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from src.main import log_http_exception


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
