import typing

from zuu.stdpkg.typing import is_typedict


class TestIsTypedict:
    def test_valid_typedict(self):
        class ValidTypeDict(typing.TypedDict):
            name: str
            age: int

        obj = {"name": "John", "age": 30}
        assert is_typedict(obj, ValidTypeDict) == ValidTypeDict

    def test_invalid_typedict(self):
        class ValidTypeDict(typing.TypedDict):
            name: str
            age: int

        obj = {"name": "John", "age": "30"}  # age should be int, not str
        assert is_typedict(obj, ValidTypeDict) is None

    def test_multiple_choices(self):
        class TypeDict1(typing.TypedDict):
            name: str
            age: int

        class TypeDict2(typing.TypedDict):
            title: str
            year: int

        obj1 = {"name": "John", "age": 30}
        obj2 = {"title": "Movie", "year": 2023}

        assert is_typedict(obj1, TypeDict1, TypeDict2) == TypeDict1
        assert is_typedict(obj2, TypeDict1, TypeDict2) == TypeDict2

    def test_non_dict_object(self):
        class ValidTypeDict(typing.TypedDict):
            name: str

        obj = ["not", "a", "dict"]
        assert is_typedict(obj, ValidTypeDict) is None

    def test_invalid_choice(self):
        class ValidTypeDict(typing.TypedDict):
            name: str

        invalid_choice = dict  # Not a TypedDict
        obj = {"name": "John"}
        assert is_typedict(obj, invalid_choice) is None

    def test_partial_match(self):
        class FullTypeDict(typing.TypedDict):
            name: str
            age: int
            city: str

        obj = {"name": "John", "age": 30}  # Missing 'city'
        assert is_typedict(obj, FullTypeDict) is None

    def test_extra_keys(self):
        class PartialTypeDict(typing.TypedDict, total=False):
            name: str
            age: int

        obj = {"name": "John", "age": 30, "city": "New York"}  # Extra 'city' key
        assert is_typedict(obj, PartialTypeDict) == PartialTypeDict
