import collections.abc
from typing import TypeVar, Type, Union, Tuple, List, Mapping, Dict, NamedTuple, Any


def _origin(expected_type: Any) -> Any:
    if hasattr(expected_type, "__origin__"):
        return expected_type.__origin__
    return None


def _check_union(expected_type: Any, raw_value: Any) -> Tuple[bool, Any]:
    for arg in expected_type.__args__:
        ok, parsed_val = _check_type(arg, raw_value)
        if ok:
            return ok, parsed_val
    # if we get here, none of the Union arguments matched
    return False, None


def _check_tuple(expected_type: Any, raw_value: Any) -> Tuple[bool, Any]:
    if not isinstance(raw_value, collections.abc.Iterable):
        return False, None

    raw_list = list(raw_value)
    result: Tuple = ()
    for i, arg in enumerate(expected_type.__args__):
        ok, parsed_val = _check_type(arg, raw_list[i])
        if not ok:
            return False, None
        result += (parsed_val,)
    return True, result


def _check_list(expected_type: Any, raw_value: Any) -> Tuple[bool, Any]:
    if not isinstance(raw_value, collections.abc.Iterable):
        return False, None

    list_type = expected_type.__args__[0]
    result: List = []
    for list_value in raw_value:
        ok, parsed_val = _check_type(list_type, list_value)
        if not ok:
            return False, None
        result.append(parsed_val)
    return True, result


def _check_type(expected_type: Any, raw_value: Any) -> Tuple[bool, Any]:
    # TODO(fyhuang): recurse on nested types
    if _origin(expected_type) == Union:
        return _check_union(expected_type, raw_value)
    elif _origin(expected_type) == Tuple:
        return _check_tuple(expected_type, raw_value)
    elif _origin(expected_type) == List:
        return _check_list(expected_type, raw_value)
    elif not isinstance(raw_value, expected_type):
        return False, None
    return True, raw_value


ObjT = TypeVar("ObjT")
def mapping_to_nt(mapping: Mapping[str, Any], nt_class: Type[ObjT], **options) -> ObjT:
    parsed_fields: Dict[str, Any] = {}
    for mk, mv in mapping.items():
        if mk not in nt_class.__annotations__:
            # TODO(fyhuang): support option to ignore unknown keys
            raise ValueError("Unknown key/value: {}, {}".format(mk, mv))

        nt_type = nt_class.__annotations__[mk]
        ok, parsed_val = _check_type(nt_type, mv)
        if not ok:
            raise TypeError("Expected {} to be of type {}".format(mk, nt_type))

        parsed_fields[mk] = parsed_val

    return nt_class(**parsed_fields) # type: ignore

def nt_to_mapping():
    pass
