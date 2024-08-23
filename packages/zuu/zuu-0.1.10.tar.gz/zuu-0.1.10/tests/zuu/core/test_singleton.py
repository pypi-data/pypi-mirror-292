import pytest
from zuu.core.singleton import var_based_singleton_metaclass


class TestVarSingleton:
    def test_creation(self):
        SingletonMetaclassWithId = var_based_singleton_metaclass()
        assert isinstance(SingletonMetaclassWithId, type)

    def test_missing_id_attribute(self):
        SingletonMetaclassWithId = var_based_singleton_metaclass()

        class TestClass(metaclass=SingletonMetaclassWithId):
            pass

        with pytest.raises(
            AttributeError, match="TestClass must have an '__id__' attribute"
        ):
            TestClass()

    def test_instance_creation(self):
        SingletonMetaclassWithId = var_based_singleton_metaclass()

        class TestClass(metaclass=SingletonMetaclassWithId):
            __id__ = "test_id"

            def __init__(self, test_id):
                self.test_id = test_id

        instance1 = TestClass(test_id="1")
        instance2 = TestClass(test_id="1")
        instance3 = TestClass(test_id="2")

        assert instance1 is instance2
        assert instance1 is not instance3

    def test_multiple_classes(self):
        class TestClass1(metaclass=var_based_singleton_metaclass()):
            __id__ = "id1"

            def __init__(self, id1):
                self.id1 = id1

        class TestClass2(metaclass=var_based_singleton_metaclass()):
            __id__ = "id2"

            def __init__(self, id2):
                self.id2 = id2

        instance1 = TestClass1(id1="1")
        instance2 = TestClass2(id2="1")

        assert instance1 is not instance2
        assert instance1 is TestClass1(id1="1")
        assert instance2 is TestClass2(id2="1")
