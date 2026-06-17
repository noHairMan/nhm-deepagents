from rainy.exceptions import RainyError


class TestExceptions:
    def test_rainy_error(self):
        """测试 RainyError 能够被正常抛出和捕获"""
        try:
            raise RainyError("test error")
        except RainyError as e:
            assert str(e) == "test error"
