import uuid

from fragile.utils.uid import is_valid_uuid, to_hex


class TestUid:
    def test_to_hex_converts_supported_values(self) -> None:
        value = uuid.UUID("12345678-1234-5678-1234-567812345678")

        assert to_hex(None) is None
        assert to_hex(255) == "ff"
        assert to_hex(value) == value.hex
        assert to_hex(value.hex) == value.hex
        assert to_hex("1234-5678") == "12345678"
        assert to_hex(value.int) == value.hex
        assert to_hex(value.bytes) == str(value.bytes)

    def test_is_valid_uuid(self) -> None:
        assert is_valid_uuid("12345678-1234-5678-1234-567812345678")
        assert not is_valid_uuid("not-a-uuid")
