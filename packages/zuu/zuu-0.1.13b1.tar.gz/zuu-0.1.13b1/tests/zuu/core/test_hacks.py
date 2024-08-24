import pytest
import inspect
from src.zuu.core.hacks import get_caller_info, get_caller_instance, get_self_name

class TestGetSelfName:
    def test_get_self_name_direct_call(self):
        def dummy_function():
            return get_self_name()
        assert dummy_function() == 'dummy_function'

    def test_get_self_name_nested_call(self):
        def outer_function():
            def inner_function():
                return get_self_name()
            return inner_function()
        assert outer_function() == 'inner_function'

    def test_get_self_name_lambda(self):
        def lambda_function():
            return (lambda: get_self_name())()
        assert lambda_function() == '<lambda>'

    def test_get_self_name_class_method(self):
        class DummyClass:
            def method(self):
                return get_self_name()
        dummy_instance = DummyClass()
        assert dummy_instance.method() == 'method'

    def test_get_self_name_static_method(self):
        class DummyClass:
            @staticmethod
            def static_method():
                return get_self_name()
        assert DummyClass.static_method() == 'static_method'

    def test_get_self_name_class_method_nested(self):
        class DummyClass:
            def outer_method(self):
                def inner_method():
                    return get_self_name()
                return inner_method()
        dummy_instance = DummyClass()
        assert dummy_instance.outer_method() == 'inner_method'
        
class TestGetCallerName:
    def test_get_caller_info_direct_call(self):
        def dummy_function():
            return get_caller_info()
        
        res = dummy_function()
        # Updated assertion to match the new behavior
        assert res['file'].endswith('test_hacks.py')
        assert res['class'] == 'TestGetCallerName'
        assert res['method'] == 'test_get_caller_info_direct_call'

    def test_get_caller_info_nested_call(self):
        def outer_function():
            def inner_function():
                return get_caller_info()
            return inner_function()
        res = outer_function()
        assert res['file'].endswith('test_hacks.py')
        assert res['method'] == 'outer_function'

    def test_get_caller_info_lambda(self):
        def lambda_function():
            return (lambda: get_caller_info())()
        
        res = lambda_function()
        assert res['file'].endswith('test_hacks.py')
        assert res['method'] == 'lambda_function'

    def test_get_caller_info_class_method(self):
        class DummyClass:
            def method(self):
                return get_caller_info()
        dummy_instance = DummyClass()
        res = dummy_instance.method()
        assert res['file'].endswith('test_hacks.py')
        assert res['class'] == 'TestGetCallerName'
        assert res['method'] == 'test_get_caller_info_class_method'

    def test_get_caller_info_static_method(self):
        class DummyClass:
            @staticmethod
            def static_method():
                return get_caller_info()
        res = DummyClass.static_method()
        assert res['file'].endswith('test_hacks.py')
        assert res['class'] == 'TestGetCallerName'
        assert res['method'] == 'test_get_caller_info_static_method'

    def test_get_caller_info_class_method_nested(self):
        class DummyClass:
            def outer_method(self):
                def inner_method():
                    return get_caller_info()
                return inner_method()
        dummy_instance = DummyClass()
        res = dummy_instance.outer_method()
        assert res['file'].endswith('test_hacks.py')
        assert res['class'] == 'DummyClass'
        assert res['method'] == 'outer_method'

    def test_get_caller_info_module_level(self):
        result = get_caller_info()
        assert result['file'].endswith('python.py')
        assert result['method'] == 'pytest_pyfunc_call'

        
class TestGetCallerInstance:
    def test_get_caller_instance_method(self):
        class DummyClass:
            def method(self):
                return get_caller_instance()
        dummy_instance = DummyClass()
        assert dummy_instance.method() is self

    def test_get_caller_instance_class_method(self):
        class DummyClass:
            @classmethod
            def class_method(cls):
                return get_caller_instance()
        assert DummyClass.class_method() is self

    def test_get_caller_instance_static_method(self):
        class DummyClass:
            @staticmethod
            def static_method():
                return get_caller_instance()
        assert DummyClass.static_method() is self

    def test_get_caller_instance_module_level_function(self):
        result = get_caller_instance()
        assert result is None

    def test_get_caller_instance_nested_instance_method(self):
        class DummyClass:
            def outer_method(self):
                def inner_method():
                    return get_caller_instance()
                return inner_method()
        dummy_instance = DummyClass()
        assert dummy_instance.outer_method() is dummy_instance

    def test_get_caller_instance_nested_class_method(self):
        class DummyClass:
            @classmethod
            def outer_class_method(cls):
                def inner_class_method():
                    return get_caller_instance()
                return inner_class_method()
        assert DummyClass.outer_class_method() is DummyClass

