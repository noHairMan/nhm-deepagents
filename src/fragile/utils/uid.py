import uuid


def to_hex(num):
    """

    将给定的数值转换为其十六进制表示。

    参数:
        - num (int, uuid.UUID, str, None): 需要转换的数值。可以是整数、UUID对象、无破折号的十六进制字符串，或None。

    返回:
        - str: 转换后的十六进制字符串。如果输入为None，则返回None。

    此函数根据输入数值的类型，采用不同策略进行转换：
        - 对于整数（int），使用内置的hex函数并去掉前缀'0x'。
        - 对于UUID对象，直接调用其hex属性获取十六进制字符串。
        - 对于无破折号的十六进制字符串，直接返回。
        - 其它情况尝试将其转换为合适的格式，若失败则原样返回。

    示例:
        1. to_hex(255) 返回 'ff'
        2. to_hex(uuid.uuid4()) 返回如 '123e4567e89b12d3a456426655440000'
        3. to_hex('1234567890abcdef') 返回 '1234567890abcdef'
        4. to_hex(None) 返回 None

    注意:
        - 若输入为非标准格式，可能导致结果不符合预期。
        - 输入字符串若有破折号，不保证正确处理。

    """
    if num is None:
        return None
    elif isinstance(num, int):
        return hex(num)[2:]
    elif isinstance(num, uuid.UUID):
        return num.hex
    elif isinstance(num, str):
        return num.replace("-", "")
    return f"{num}"


def is_valid_uuid(num):
    try:
        uuid.UUID(num)
        return True
    except ValueError:
        return False
