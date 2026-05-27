import json

from fastapi import Request
from fastapi.responses import JSONResponse

from rainy.conf import settings
from rainy.models.response import BaseResponse


async def unify_response_format(request: Request, call_next):
    """
    统一响应格式中间件
    """
    response = await call_next(request)

    if request.url.path in settings.UNIFY_RESPONSE_FORMAT_EXCLUDE:
        return response

    # 仅处理成功状态且为 JSON 的响应
    if response.status_code != 200 or "application/json" not in response.headers.get("Content-Type", ""):
        return response

    # 读取响应体
    body = b"".join([chunk async for chunk in response.body_iterator])
    data = json.loads(body)
    # 包装数据
    wrapped = BaseResponse.success(data=data).model_dump()
    return JSONResponse(content=wrapped)
