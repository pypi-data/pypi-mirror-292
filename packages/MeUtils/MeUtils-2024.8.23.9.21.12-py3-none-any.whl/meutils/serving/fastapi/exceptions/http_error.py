import json
import traceback

from fastapi import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi.exceptions import RequestValidationError, HTTPException

from meutils.notice.feishu import send_message


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

    send_message(
        await request.json(),
        title="chatfire_api_exception_handler",
        url="https://open.feishu.cn/open-apis/bot/v2/hook/79fc258f-46a9-419e-b131-1d79b3d0bcff"
    )

    send_message(
        content,
        title="chatfire_api_exception_handler",
        url="https://open.feishu.cn/open-apis/bot/v2/hook/79fc258f-46a9-419e-b131-1d79b3d0bcff"
    )

    send_message(
        content_detail,
        title="chatfire_api_exception_handler",
        url="https://open.feishu.cn/open-apis/bot/v2/hook/79fc258f-46a9-419e-b131-1d79b3d0bcff"
    )

    # send_message
    return JSONResponse(
        content=content,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


if __name__ == '__main__':
    pass
