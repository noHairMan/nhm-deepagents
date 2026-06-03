from rainy.models.constants import BusinessCode
from rainy.models.response import BaseResponse


class TestModelsResponse:
    def test_base_response_success(self):
        resp = BaseResponse.success(data={"key": "value"})
        assert resp.code == BusinessCode.SUCCESS
        assert resp.data == {"key": "value"}
        assert resp.message == BusinessCode.SUCCESS.label

    def test_base_response_error(self):
        resp = BaseResponse.error(code=BusinessCode.ERROR, message="Custom Error")
        assert resp.code == BusinessCode.ERROR
        assert resp.message == "Custom Error"
        assert resp.data is None

    def test_base_response_error_default(self):
        resp = BaseResponse.error()
        assert resp.code == BusinessCode.ERROR
        assert resp.message == BusinessCode.ERROR.label
