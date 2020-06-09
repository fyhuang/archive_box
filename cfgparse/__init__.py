import collections.abc
import typing
from typing import TypeVar, Type, Optional, Union, Tuple, List, Dict, NamedTuple, Any


class ParseError(Exception):
    pass


class _Result(NamedTuple):
    error: Optional[Exception]
    cast_value: Any

    @staticmethod
    def value(val: Any) -> '_Result':
        return _Result(None, val)

    @staticmethod
    def parse_error(error_str: str) -> '_Result':
        return _Result(ParseError(error_str), None)

    def ok(self) -> bool:
        return self.error is None


def _origin(expected_type) -> Any:
    if hasattr(expected_type, "__origin__"):
        return expected_type.__origin__
    return None


def _cast_to_union(expected_type, raw_value) -> _Result:
    for arg in expected_type.__args__:
        tcr = _cast_to_type(arg, raw_value)
        if tcr.ok():
            return tcr
    # if we get here, none of the Union arguments matched
    return _Result.parse_error("Expected {}, got {}".format(expected_type, raw_value))


def _cast_to_tuple(expected_type, raw_value) -> _Result:
    if not isinstance(raw_value, collections.abc.Iterable):
        return _Result.parse_error("Expected {} but value {} is not iterable".format(expected_type, raw_value))

    raw_list = list(raw_value)
    cast_tuple: Tuple = ()
    for i, arg in enumerate(expected_type.__args__):
        tcr = _cast_to_type(arg, raw_list[i])
        if not tcr.ok():
            return tcr
        cast_tuple += (tcr.cast_value,)
    return _Result.value(cast_tuple)


def _cast_to_list(expected_type, raw_value) -> _Result:
    if not isinstance(raw_value, collections.abc.Iterable):
        return _Result.parse_error("Expected {} but value {} is not iterable".format(expected_type, raw_value))

    list_type = expected_type.__args__[0]
    cast_list: List = []
    for list_value in raw_value:
        tcr = _cast_to_type(list_type, list_value)
        if not tcr.ok():
            return tcr
        cast_list.append(tcr.cast_value)
    return _Result.value(cast_list)


def _cast_to_dict(expected_type, raw_value) -> _Result:
    if not isinstance(raw_value, collections.abc.Mapping):
        return _Result.parse_error("Expected {} but value {} is not a mapping".format(expected_type, raw_value))

    dict_key_type = expected_type.__args__[0]
    dict_value_type = expected_type.__args__[1]
    cast_dict: Dict = {}
    for key, value in raw_value.items():
        key_tcr = _cast_to_type(dict_key_type, key)
        if not key_tcr.ok():
            return key_tcr

        value_tcr = _cast_to_type(dict_value_type, value)
        if not value_tcr.ok():
            return value_tcr

        cast_dict[key_tcr.cast_value] = value_tcr.cast_value
        
    return _Result.value(cast_dict)


def _cast_to_namedtuple(expected_type, raw_value) -> _Result:
    if not isinstance(raw_value, collections.abc.Mapping):
        return _Result.parse_error("Expected {} but value {} is not a mapping".format(expected_type, raw_value))

    cast_fields: Dict[str, Any] = {}
    for key, value in raw_value.items():
        if key not in expected_type.__annotations__:
            # TODO(fyhuang): support option to ignore unknown keys
            return _Result.parse_error("Expected {} but encountered unknown key/value: {}, {}".format(expected_type, key, value))

        nt_type = expected_type.__annotations__[key]
        tcr = _cast_to_type(nt_type, value)
        if not tcr.ok():
            return tcr

        cast_fields[key] = tcr.cast_value

    return _Result.value(expected_type(**cast_fields)) # type: ignore


def _cast_to_type(expected_type: Any, raw_value: Any) -> _Result:
    if hasattr(expected_type, '__annotations__'):
        return _cast_to_namedtuple(expected_type, raw_value)
    if _origin(expected_type) == Union:
        return _cast_to_union(expected_type, raw_value)
    elif _origin(expected_type) == Tuple:
        return _cast_to_tuple(expected_type, raw_value)
    elif _origin(expected_type) == List:
        return _cast_to_list(expected_type, raw_value)
    elif _origin(expected_type) == Dict:
        return _cast_to_dict(expected_type, raw_value)
    elif not isinstance(raw_value, expected_type):
        return _Result.parse_error("Expected {}, got {}".format(expected_type, raw_value))
    return _Result.value(raw_value)


ObjT = TypeVar("ObjT")
def mapping_to_nt(mapping: typing.Mapping[str, Any], nt_class: Type[ObjT], **options) -> ObjT:
    typecast_result = _cast_to_type(nt_class, mapping)
    if typecast_result.error is not None:
        raise typecast_result.error
    return typecast_result.cast_value


def nt_to_mapping():
    raise NotImplementedError()
