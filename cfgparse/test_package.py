import unittest
from typing import Optional, Tuple, List, Dict, NamedTuple

from . import *


class NestedNt(NamedTuple):
    n_a: float
    n_b: str

class TestNt(NamedTuple):
    f_str: str = ""
    f_int: int = 0
    f_optional: Optional[int] = None
    f_tuple: Tuple[int, float] = (0, 0.0)
    f_list: List[str] = []
    f_dict: Dict[str, int] = {}
    f_optional_nested: Optional[NestedNt] = None
    f_list_nested: List[NestedNt] = []
    f_dict_nested: Dict[int, NestedNt] = {}

class MappingToNtTests(unittest.TestCase):
    def test_wrong_primitive(self) -> None:
        with self.assertRaises(ParseError):
            mapping_to_nt(
                {"f_str": 123, "f_int": "hello"},
                TestNt
            )

    def test_primitive(self) -> None:
        nt = mapping_to_nt({"f_str": "hello", "f_int": 123}, TestNt)
        self.assertEqual(TestNt(f_str="hello", f_int=123), nt)

    def test_optional(self) -> None:
        nt = mapping_to_nt({"f_optional": None}, TestNt)
        self.assertEqual(TestNt(f_optional=None), nt)
        nt = mapping_to_nt({"f_optional": 100}, TestNt)
        self.assertEqual(TestNt(f_optional=100), nt)

    def test_tuple(self) -> None:
        nt = mapping_to_nt({"f_tuple": [1, 2.0]}, TestNt)
        self.assertEqual(TestNt(f_tuple=(1, 2.0)), nt)

    def test_list(self) -> None:
        nt = mapping_to_nt({"f_list": ["a", "b"]}, TestNt)
        self.assertEqual(TestNt(f_list=["a", "b"]), nt)

    def test_dict(self) -> None:
        nt = mapping_to_nt({"f_dict": {"a": 1}}, TestNt)
        self.assertEqual(TestNt(f_dict={"a": 1}), nt)

    def test_optional_nested(self) -> None:
        nt = mapping_to_nt({"f_optional_nested": {"n_a": 2.0, "n_b": "abc"}}, TestNt)
        self.assertEqual(TestNt(f_optional_nested=NestedNt(2.0, "abc")), nt)

    def test_list_nested(self) -> None:
        nt = mapping_to_nt({"f_list_nested": [{"n_a": 2.0, "n_b": "abc"}]}, TestNt)
        self.assertEqual(TestNt(f_list_nested=[NestedNt(2.0, "abc")]), nt)

    def test_dict_nested(self) -> None:
        nt = mapping_to_nt({"f_dict_nested": {23: {"n_a": 2.0, "n_b": "abc"}}}, TestNt)
        self.assertEqual(TestNt(f_dict_nested={23: NestedNt(2.0, "abc")}), nt)
