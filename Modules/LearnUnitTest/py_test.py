def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 5

class TestClass1:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")


class TestClass2:
    def tes_one(self):
        x = "this"
        assert "h" in x

    def tes_two(self):
        x = "hello"
        assert hasattr(x, "check")