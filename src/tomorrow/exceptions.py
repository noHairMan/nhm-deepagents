class TomorrowError(Exception):
    """Tomorrow 应用的基础异常类"""

    pass


class TomorrowRuntimeError(TomorrowError, RuntimeError):
    """Tomorrow 应用的 RuntimeError"""

    pass


class TomorrowBackendError(TomorrowError):
    """Tomorrow 后端相关的异常"""

    pass


class TomorrowModelError(TomorrowError):
    """Tomorrow 模型相关的异常"""

    pass


class TomorrowStoreError(TomorrowError):
    """Tomorrow 存储相关的异常"""

    pass


class TomorrowCheckpointError(TomorrowError):
    """Tomorrow 检查点相关的异常"""

    pass
