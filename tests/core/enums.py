from tomorrow.core.enums import Choices, IntChoices, TextChoices


class TestChoices:
    def test_label(self):
        class TestEnum(Choices):
            A = "a", "Alpha"

        enum = TestEnum.A
        assert enum.value == "a"
        assert enum.label == "Alpha"

    def test_no_label(self):
        class TestEnum(Choices):
            A = "a"

        enum = TestEnum.A
        assert enum.label == "a"
        assert enum.value == "a"

    def test_choices_list(self):
        class TestEnum(Choices):
            A = "a", "Alpha"
            B = "b", "Beta"

        assert list(TestEnum) == [TestEnum.A, TestEnum.B]
        assert TestEnum.A.label == "Alpha"
        assert TestEnum.B.label == "Beta"

    def test_membership(self):
        class TestEnum(Choices):
            A = "a", "Alpha"

        assert TestEnum.A in TestEnum
        assert "a" in TestEnum
        assert "b" not in TestEnum

    def test_integer_choices(self):
        class TestEnum(Choices):
            ONE = 1, "One"
            TWO = 2, "Two"

        assert TestEnum.ONE.value == 1
        assert TestEnum.ONE.label == "One"
        assert TestEnum.choices == [(1, "One"), (2, "Two")]


class TestChoicesMeta:
    def test_choices_property(self):
        class TestEnum(Choices):
            A = "a", "Alpha"
            B = "b", "Beta"

        assert TestEnum.choices == [("a", "Alpha"), ("b", "Beta")]

    def test_values_property(self):
        class TestEnum(Choices):
            A = "a", "Alpha"
            B = "b", "Beta"

        assert TestEnum.values == ["a", "b"]

    def test_values_list_membership(self):
        class TestEnum(Choices):
            A = "a", "Alpha"
            B = "b", "Beta"

        assert "a" in TestEnum.values
        assert "c" not in TestEnum.values

    def test_labels_property(self):
        class TestEnum(Choices):
            A = "a", "Alpha"
            B = "b", "Beta"

        assert TestEnum.labels == ["Alpha", "Beta"]


class TestIntChoices:
    def test_int_choices(self):
        class Status(IntChoices):
            ACTIVE = 1, "激活"
            INACTIVE = 0, "未激活"

        assert Status.ACTIVE == 1
        assert Status.ACTIVE.value == 1
        assert Status.ACTIVE.label == "激活"
        assert Status.values == [1, 0]
        assert Status.labels == ["激活", "未激活"]
        assert Status.choices == [(1, "激活"), (0, "未激活")]
        assert isinstance(Status.ACTIVE, int)


class TestTextChoices:
    def test_text_choices(self):
        class Color(TextChoices):
            RED = "R", "红色"
            BLUE = "B", "蓝色"

        assert Color.RED == "R"
        assert Color.RED.value == "R"
        assert Color.RED.label == "红色"
        assert Color.values == ["R", "B"]
        assert Color.labels == ["红色", "蓝色"]
        assert Color.choices == [("R", "红色"), ("B", "蓝色")]
        assert isinstance(Color.RED, str)
