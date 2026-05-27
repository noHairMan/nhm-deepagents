from tomorrow.core.enums import IntChoices


class BusinessCode(IntChoices):
    """
    业务状态码
    """

    SUCCESS = 0, "成功"
    ERROR = 1, "错误"
    NOT_FOUND = 2, "未找到"
    UNAUTHORIZED = 3, "未授权"
    FORBIDDEN = 4, "已禁止"
    VALIDATION_ERROR = 5, "验证错误"
