from typing import Any, Dict, List, Tuple

from src.utils.parse import parse_version_string


def filter_by_version(
    max_version: str, minion_data: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    max_version_major, max_version_minor = parse_version_string(max_version)
    all_minions = minion_data.items()
    unresponsive_minions = list(
        map(
            lambda item: item[0],
            filter(lambda item: "saltversion" not in item[1], all_minions),
        )
    )

    responsive_minions = list(
        filter(lambda item: "saltversion" in item[1], all_minions)
    )
    parsed_minions = list(
        map(
            lambda item: (item[0], parse_version_string(item[1].get("saltversion"))),
            responsive_minions,
        )
    )
    updatable_minions = list(
        map(
            lambda item: {item[0]: f"{item[1][0]}.{item[1][1]}"},
            filter(
                lambda item: item[1][0] < max_version_major
                and item[1][1] < max_version_minor,
                parsed_minions,
            ),
        )
    )
    higher_version_minions = list(
        map(
            lambda item: {item[0]: f"{item[1][0]}.{item[1][1]}"},
            filter(
                lambda item: item[1][0] == max_version_major
                and item[1][1] > max_version_minor,
                parsed_minions,
            ),
        )
    )

    return updatable_minions, higher_version_minions, unresponsive_minions


def transform_minion_data(max_version: str, data: List[Dict[str, Any]]) -> List:
    return list(map(lambda d: filter_by_version(max_version, d), data))
