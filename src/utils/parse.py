import operator
from functools import reduce
from typing import Any, Callable, Dict, List, Optional, Tuple


def parse_version_string(version_str: str) -> Tuple[int, int]:
    try:
        parts = version_str.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        return major, minor
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid version string format: {version_str}") from e


# def get_nested_value(
#     data: Dict[str, Any], path: List[str], default: Optional[Any] = None
# ):
#     try:
#         return reduce(operator.getitem, path, data)
#     except (KeyError, TypeError, IndexError):
#         return default
#
#
# def __create_row_from_object(
#     obj_dict: Dict[str, Any],
#     column_map: Dict[str, Tuple[List[str], Optional[Callable]]],
# ) -> Dict[str, Any]:
#     row = {}
#     for header, (path, formatter) in column_map.items():
#         value = get_nested_value(obj_dict, path)
#         row[header] = formatter(value) if formatter else value
#     return row
#
#
# def parse_objects(
#     object_list: List[Any],
#     column_map: Dict[str, Tuple[List[str], Optional[Callable]]],
# ) -> Tuple[List[str], List[Dict[str, Any]]]:
#     if not object_list:
#         return [], []
#     headers = list(column_map.keys())
#     rows = [__create_row_from_object(vars(obj), column_map) for obj in object_list]
#     return headers, rows


def get_nested_attribute(obj: Any, path: str, default: Optional[Any] = None) -> Any:
    attributes = path.split(".")
    current_obj = obj
    for attr in attributes:
        if current_obj is None:
            return default
        current_obj = getattr(current_obj, attr, default)
    return current_obj


def __create_row(
    obj: Any, column_map: Dict[str, Tuple[str, Optional[Callable]]]
) -> Dict[str, Any]:
    return {
        header: (
            formatter(get_nested_attribute(obj, path))
            if formatter
            else get_nested_attribute(obj, path)
        )
        for header, (path, formatter) in column_map.items()
    }


def create_parser(
    column_map: Dict[str, Tuple[str, Optional[Callable]]],
) -> Callable[[List[Any]], Tuple[List[str], List[Dict[str, Any]]]]:
    def parser(object_list: List[Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        if not object_list:
            return [], []
        headers = list(column_map.keys())
        rows = [__create_row(obj, column_map) for obj in object_list]
        return headers, rows

    return parser
