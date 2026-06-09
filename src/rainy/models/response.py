from typing import Optional, TypeVar

from pydantic import BaseModel

from rainy.models.constants import BusinessCode

T = TypeVar("T")


class BaseResponse[T](BaseModel):
    """
    业务响应基类
    """

    code: int
    message: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Optional[T] = None, message: Optional[str] = None) -> BaseResponse[T]:
        return cls(code=BusinessCode.SUCCESS, message=message or BusinessCode.SUCCESS.label, data=data)

    @classmethod
    def error(
        cls,
        code: BusinessCode = BusinessCode.ERROR,
        message: Optional[str] = None,
        data: Optional[T] = None,
    ) -> BaseResponse[T]:
        return cls(code=code, message=message or code.label, data=data)
