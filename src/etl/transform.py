import logging
import re

from src.utils.parse import parse_version_string

log = logging.getLogger(__name__)


def filter_by_version(max_version, minion_data):
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


def transform_minion_data(max_version, data):
    return list(map(lambda d: filter_by_version(max_version, d), data))


def extract_core_os_pattern(text: str, delimiter="|"):
    if not text:
        return ""
    os_name_part = text.split(delimiter)[0]
    rules = [
        {
            "name": "Debian",
            "pattern": re.compile(r"(Debian).*?(\d+)", re.IGNORECASE),
            "formatter": r"\1 \2",
        },
        {
            "name": "Ubuntu",
            "pattern": re.compile(r"(Ubuntu).*?(\d{2}\.\d{2})", re.IGNORECASE),
            "formatter": r"\1 \2",
        },
        {
            "name": "CentOS",
            "pattern": re.compile(r"(CentOS).*?(\d{1})", re.IGNORECASE),
            "formatter": r"\1 \2",
        },
        {
            "name": "Oracle",
            "pattern": re.compile(r"(Oracle).*?(\d{1})", re.IGNORECASE),
            "formatter": r"\1 \2",
        },
        {
            "name": "Windows Server",
            "pattern": re.compile(r"(Windows Server \d{4})", re.IGNORECASE),
            "formatter": r"\1",
        },
        {
            "name": "Windows",
            "pattern": re.compile(r"(Windows).*?(\d{2})", re.IGNORECASE),
            "formatter": r"\1 \2",
        },
        {
            "name": "XCP-ng",
            "pattern": re.compile(r"(XCP-ng).*?(\d{1}\.\d{1})", re.IGNORECASE),
            "formatter": r"\1 \2",
        },
    ]
    for rule in rules:
        match = rule["pattern"].search(os_name_part)
        if match:
            refactored_term = match.expand(rule["formatter"])
            log.info(
                f"Matched rule '{rule['name']}' on '{os_name_part}' : '{refactored_term}'"
            )
            return refactored_term

    log.warning(
        f"No specific rule matched for '{os_name_part}'. Returning a trimmed version."
    )
    return os_name_part.strip() if os_name_part else None


def flatten_to_target(data, target_key="id"):
    def is_complex(value):
        if isinstance(value, dict) and value:
            return True
        if isinstance(value, list) and value:
            return True
        return False

    if isinstance(data, dict) and "data" in data and len(data) == 1:
        return flatten_to_target(data["data"], target_key)

    if isinstance(data, list):
        return [
            flatten_to_target(item, target_key) for item in data if item is not None
        ]

    if isinstance(data, dict):
        has_target = target_key in data
        has_complex_children = any(is_complex(v) for v in data.values())
        if has_target and not has_complex_children:
            return data[target_key]
        new_dict = {}
        if has_target:
            new_dict[target_key] = data[target_key]
        for key, value in data.items():
            if key == target_key:
                continue
            if is_complex(value):
                processed_value = flatten_to_target(value, target_key)
                if processed_value not in (None, {}, []):
                    new_dict[key] = processed_value
        if not new_dict:
            return None

        return new_dict

    return data
