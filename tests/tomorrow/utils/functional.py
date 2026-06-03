import copy

import pytest

from tomorrow.utils.functional import (
    LazyObject,
    SimpleLazyObject,
    cached_property,
    classproperty,
    import_string,
    keep_lazy,
    keep_lazy_text,
    lazy,
    lazystr,
    partition,
)


class TestFunctional:
    def test_cached_property(self):
        class A:
            def __init__(self):
                self.count = 0

            @cached_property
            def prop(self):
                self.count += 1
                return self.count

        a = A()
        assert a.prop == 1
        assert a.prop == 1
        assert a.count == 1

    def test_classproperty(self):
        class A:
            @classproperty
            def prop(cls):
                return "value"

        assert A.prop == "value"

    def test_partition(self):
        def is_even(x):
            return x % 2 == 0

        false_list, true_list = partition(is_even, range(10))
        assert true_list == [0, 2, 4, 6, 8]
        assert false_list == [1, 3, 5, 7, 9]

    def test_import_string(self):
        import logging

        assert import_string("logging.Logger") is logging.Logger
        with pytest.raises(ImportError):
            import_string("non_existent_module.Class")
        with pytest.raises(ImportError):
            import_string("logging.NonExistentClass")

    def test_simple_lazy_object(self):
        def setup():
            return "real_value"

        lazy_obj = SimpleLazyObject(setup)
        assert lazy_obj == "real_value"
        assert str(lazy_obj) == "real_value"
        assert repr(lazy_obj).endswith("real_value'>")

    def test_simple_lazy_object_copy(self):
        def setup():
            return [1, 2, 3]

        lazy_obj = SimpleLazyObject(setup)
        copied = copy.copy(lazy_obj)
        assert copied == [1, 2, 3]
        assert copied is not lazy_obj

    def test_lazy_object(self):
        class RealObject:
            def __init__(self):
                self.value = 42

        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = RealObject()

        lazy_obj = MyLazyObject()
        assert lazy_obj.value == 42
        lazy_obj.value = 43
        assert lazy_obj.value == 43
        del lazy_obj.value
        with pytest.raises(AttributeError):
            print(lazy_obj.value)

        # Test __reduce__
        red = lazy_obj.__reduce__()
        from tomorrow.utils.functional import unpickle_lazyobject

        assert red[0] == unpickle_lazyobject

        # Test __copy__
        lazy_obj = MyLazyObject()
        cp = copy.copy(lazy_obj)
        assert cp.value == 42

        # Test __deepcopy__
        lazy_obj = MyLazyObject()
        memo = {}
        dcp = copy.deepcopy(lazy_obj, memo)
        assert dcp.value == 42

    def test_lazy_proxy_ops(self):
        def func(x):
            return x

        lazy_func = lazy(func, int)
        p1 = lazy_func(5)
        p2 = lazy_func(10)

        assert p1 + p2 == 15
        assert p1 < p2
        assert p1 <= p2
        assert p2 > p1
        assert p2 >= p1
        assert p1 == 5
        assert p1 != 6
        assert hash(p1) == hash(5)
        assert format(p1, "d") == "5"
        assert p1 % 2 == 1
        assert p1 * 2 == 10
        assert 1 + p1 == 6

    def test_lazy_proxy_more_ops(self):
        def func(x):
            return x

        lazy_func = lazy(func, str)
        p = lazy_func("hello")
        assert p + " world" == "hello world"

        lazy_int = lazy(func, int)(5)
        assert lazy_int + 1 == 6
        assert 1 + lazy_int == 6

        # Test __mod__
        lazy_fmt = lazy(func, str)("hello %s")
        assert lazy_fmt % "world" == "hello world"

    def test_lazy_proxy_unpickle(self):
        from tomorrow.utils.functional import _lazy_proxy_unpickle

        res = _lazy_proxy_unpickle(lambda x: x, (5,), {})
        assert res == 5

    def test_simple_lazy_object_deepcopy(self):
        obj = SimpleLazyObject(lambda: {"a": 1})
        cp = copy.deepcopy(obj)
        assert cp == {"a": 1}

    def test_lazy_object_copy_uninitialized(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = "initialized"

        lazy_obj = MyLazyObject()
        cp = copy.copy(lazy_obj)
        from tomorrow.utils.functional import empty

        assert cp._wrapped is empty

    def test_simple_lazy_object_copy_uninitialized(self):
        def setup():
            return "real"

        lazy_obj = SimpleLazyObject(setup)
        cp = copy.copy(lazy_obj)
        assert cp == "real"

    def test_lazy_proxy_misc(self):
        def func(x):
            return x

        l_list = lazy(func, list)([1, 2, 3])
        assert len(l_list) == 3
        assert 1 in l_list
        assert l_list[0] == 1
        l_list[0] = 10
        assert l_list[0] == 10
        del l_list[0]
        assert len(l_list) == 2

        l_dict = lazy(func, dict)({"a": 1})
        assert "a" in l_dict
        assert list(iter(l_dict)) == ["a"]

    def test_lazy_proxy_bool_bytes(self):
        def func(x):
            return x

        assert bool(lazy(func, bool)(True)) is True
        assert bool(lazy(func, bool)(False)) is False
        assert bytes(lazy(func, bytes)(b"hello")) == b"hello"

    def test_lazy_func(self):
        def func(x):
            return x * 2

        lazy_func = lazy(func, int)
        proxy = lazy_func(5)
        assert proxy + 1 == 11
        assert str(proxy) == "10"

    def test_lazystr(self):
        s = lazystr("hello")
        assert str(s) == "hello"

    def test_keep_lazy(self):
        @keep_lazy(str)
        def concat(a, b):
            return a + b

        lazy_a = lazystr("hello")
        result = concat(lazy_a, " world")
        assert str(result) == "hello world"

    def test_keep_lazy_text(self):
        @keep_lazy_text
        def upper(s):
            return s.upper()

        lazy_s = lazystr("hello")
        result = upper(lazy_s)
        assert str(result) == "HELLO"

    def test_cached_property_error(self):
        class A:
            prop = cached_property(lambda x: 1)

        # In Python 3.6+, __set_name__ is called automatically when the class is created.
        # To trigger the error, we need to bypass __set_name__ or call the staticmethod directly.
        with pytest.raises(TypeError, match="Cannot use cached_property instance without calling __set_name__"):
            cached_property.func(None)

    def test_cached_property_set_name_error(self):
        cp = cached_property(lambda x: 1)
        cp.__set_name__(None, "a")
        with pytest.raises(TypeError, match="Cannot assign the same cached_property to two different names"):
            cp.__set_name__(None, "b")

    def test_cached_property_none_instance(self):
        class A:
            @cached_property
            def prop(self):
                return 1

        assert isinstance(A.prop, cached_property)

    def test_classproperty_getter(self):
        class A:
            pass

        cp = classproperty(lambda cls: 1)
        A.prop = cp

        @cp.getter
        def new_prop(cls):
            return 2

        A.prop = cp
        assert A.prop == 2

    def test_lazy_proxy_deepcopy(self):
        p = lazy(lambda x: x, int)(5)
        cp = copy.deepcopy(p)
        assert cp is p

    def test_lazy_proxy_comparison_with_promise(self):
        l1 = lazy(lambda: 5, int)()
        l2 = lazy(lambda: 5, int)()
        assert l1 == l2
        assert not (l1 != l2)

        l3 = lazy(lambda: 10, int)()
        assert l1 < l3
        assert l1 <= l3
        assert l3 > l1
        assert l3 >= l1

    def test_lazy_proxy_comparison_with_promise_non_promise(self):
        l1 = lazy(lambda: 5, int)()
        assert l1 == 5
        assert l1 != 6
        assert l1 < 10
        assert l1 <= 5
        assert l1 > 2
        assert l1 >= 5

    def test_lazy_object_reduce_uninitialized(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = "init_from_reduce"

        lo = MyLazyObject()
        # Verify it's uninitialized
        from tomorrow.utils.functional import empty

        assert lo._wrapped is empty

        red = lo.__reduce__()
        from tomorrow.utils.functional import unpickle_lazyobject

        assert red[0] == unpickle_lazyobject
        assert red[1] == ("init_from_reduce",)
        assert lo._wrapped == "init_from_reduce"

    def test_lazy_object_reduce_initialized(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = "init"

        lo = MyLazyObject()
        assert lo == "init"  # force init
        red = lo.__reduce__()
        from tomorrow.utils.functional import unpickle_lazyobject

        assert red[0] == unpickle_lazyobject
        assert red[1] == ("init",)

    def test_keep_lazy_no_args_error(self):
        with pytest.raises(TypeError, match="You must pass at least one argument to keep_lazy"):
            keep_lazy()

    def test_keep_lazy_immediate(self):
        @keep_lazy(int)
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

    def test_lazy_object_delattr_error(self):
        lo = LazyObject()
        with pytest.raises(TypeError, match="can't delete _wrapped"):
            del lo._wrapped

    def test_lazy_object_not_implemented_setup(self):
        lo = LazyObject()
        with pytest.raises(NotImplementedError):
            lo._setup()

    def test_lazy_object_setattr_wrapped(self):
        lo = LazyObject()
        lo._wrapped = 1
        assert lo._wrapped == 1

    def test_lazy_object_deepcopy_uninitialized(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = "init"

        lo = MyLazyObject()
        memo = {}
        cp = copy.deepcopy(lo, memo)
        from tomorrow.utils.functional import empty

        assert cp._wrapped is empty

    def test_simple_lazy_object_repr(self):
        func = lambda: "val"
        lo = SimpleLazyObject(func)
        assert repr(lo) == f"<SimpleLazyObject: {func!r}>"
        assert lo == "val"
        assert repr(lo) == "<SimpleLazyObject: 'val'>"

    def test_simple_lazy_object_copy_uninitialized_real(self):
        func = lambda: "val"
        lo = SimpleLazyObject(func)
        cp = copy.copy(lo)
        from tomorrow.utils.functional import empty

        assert cp._wrapped is empty

    def test_simple_lazy_object_deepcopy_uninitialized(self):
        func = lambda: "val"
        lo = SimpleLazyObject(func)
        memo = {}
        cp = copy.deepcopy(lo, memo)
        from tomorrow.utils.functional import empty

        assert cp._wrapped is empty

    def test_simple_lazy_object_radd(self):
        lo = SimpleLazyObject(lambda: 5)
        assert 10 + lo == 15

    def test_unpickle_lazyobject(self):
        from tomorrow.utils.functional import unpickle_lazyobject

        assert unpickle_lazyobject("val") == "val"

    def test_import_string_errors(self):
        with pytest.raises(ImportError, match="doesn't look like a module path"):
            import_string("noproperpath")

        with pytest.raises(ImportError, match="does not define a"):
            import_string("os.non_existent_attribute")

    def test_lazy_repr(self):
        def my_func():
            return "hello"

        l = lazy(my_func, str)()
        assert repr(l) == "'hello'"

    def test_lazy_str(self):
        l = lazy(lambda: "hello", str)()
        assert str(l) == "hello"

    def test_lazy_reduce(self):
        def my_func(x):
            return x

        l = lazy(my_func, int)(5)
        red = l.__reduce__()
        assert red[1][0] == my_func
        assert red[1][1] == (5,)

    def test_lazy_object_getattr_mask(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = 1

        # We need a proxy method that has _mask_wrapped = False
        from tomorrow.utils.functional import new_method_proxy

        class ProxyClass(MyLazyObject):
            proxy_method = new_method_proxy(lambda x: x)

        lo = ProxyClass()
        with pytest.raises(AttributeError):
            _ = lo.proxy_method

    def test_lazy_object_setattr_uninitialized(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = type("Obj", (), {"attr": 0})()

        lo = MyLazyObject()
        lo.attr = 10
        assert lo.attr == 10

    def test_lazy_object_delattr_uninitialized(self):
        class Obj:
            def __init__(self):
                self.attr = 0

        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = Obj()

        lo = MyLazyObject()
        del lo.attr
        with pytest.raises(AttributeError):
            _ = lo.attr

    def test_lazy_object_copy_initialized(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = [1, 2]

        lo = MyLazyObject()
        assert lo[0] == 1  # force init
        cp = copy.copy(lo)
        assert cp == [1, 2]
        assert cp is not lo._wrapped

    def test_lazy_object_deepcopy_initialized(self):
        class MyLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = {"a": 1}

        lo = MyLazyObject()
        assert lo["a"] == 1  # force init
        cp = copy.deepcopy(lo)
        assert cp == {"a": 1}
        assert cp is not lo._wrapped

    def test_simple_lazy_object_copy_initialized(self):
        lo = SimpleLazyObject(lambda: [1, 2])
        assert lo[0] == 1  # force init
        cp = copy.copy(lo)
        assert cp == [1, 2]

    def test_simple_lazy_object_deepcopy_initialized(self):
        lo = SimpleLazyObject(lambda: {"a": 1})
        assert lo["a"] == 1  # force init
        cp = copy.deepcopy(lo)
        assert cp == {"a": 1}

    def test_cached_property_multiple_names_same_name(self):
        cp = cached_property(lambda x: 1)
        cp.__set_name__(None, "a")
        cp.__set_name__(None, "a")  # Should not raise
        assert cp.name == "a"
