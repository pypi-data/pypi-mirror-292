import json
import traceback
from functools import partial
from httpx import HTTPStatusError

from fastapi import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi.exceptions import RequestValidationError, HTTPException

from meutils.notice.feishu import send_message as _send_message

send_message = partial(
    _send_message,
    title=__name__,
    url="https://open.feishu.cn/open-apis/bot/v2/hook/79fc258f-46a9-419e-b131-1d79b3d0bcff"
)


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    # print(exc)
    content = {
        "error":
            {
                "message": f"{exc.detail}",
                "type": "http-error",
            }
    }
    return JSONResponse(
        content=content,
        status_code=exc.status_code
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def chatfire_api_exception_handler(request: Request, exc: Exception):
    content = {
        "error":
            {
                "message": f"{exc}",
                "type": "chatfire-api-error",
            },

        # "code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    content_detail = f"{traceback.format_exc()}"

    send_message([content, content_detail])

    if isinstance(exc, HTTPStatusError):
        content['error']['message'] = f"{exc}\n{exc.response.text}"
        return JSONResponse(
            content=content,
            status_code=exc.response.status_code,
        )

    # send_message
    return JSONResponse(
        content=content,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


if __name__ == '__main__':
    pass
