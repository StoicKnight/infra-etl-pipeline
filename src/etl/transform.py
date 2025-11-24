import logging
from typing import Any, Set, Dict, List, Tuple


from src.utils.parse import parse_version_string
import re

log = logging.getLogger(__name__)


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


def extract_ids_from_query(data: Dict[str, Any]) -> Dict[str, Any]:
    inner_data = data.get("data")
    if not inner_data:
        return {}
    result = {}
    special_handlers = {
        "site": _process_site,
        "device": _process_device,
        "virtual_machine": _process_vm,
    }
    for key, value in inner_data.items():
        if not isinstance(value, list):
            result[key] = set()
            continue
        handler = special_handlers.get(key, _extract_simple_ids)
        result[key] = handler(value)
    devices = inner_data.get("device", [])
    clusters = inner_data.get("cluster", [])
    if devices and len(clusters) != 1:
        matched_ids = _find_matching_clusters(devices, clusters)
        if matched_ids:
            log.debug(f"Overriding cluster IDs with matched set: {matched_ids}")
            result["cluster"] = sorted(list(matched_ids))

    return result


def _get_id(item: Dict, key: str = "id"):
    val = item.get(key)
    return str(val) if val is not None else None


def _extract_simple_ids(items: List[Dict]) -> List[str]:
    unique_ids = {
        str(item["id"])
        for item in items
        if isinstance(item, dict) and item.get("id") is not None
    }
    return sorted(list(unique_ids))


def _process_site(sites: List[Dict]) -> List[Dict]:
    processed = []
    for site in sites:
        site_id = _get_id(site)
        if not site_id:
            continue
        locations = site.get("locations", [])
        loc_ids = _extract_simple_ids(locations)
        processed.append({"id": site_id, "location": loc_ids})
    return processed


def _process_device(devices: List[Dict]) -> List[Dict]:
    processed = []
    for dev in devices:
        dev_id = _get_id(dev)
        if not dev_id:
            continue
        entry = {"id": dev_id}
        for field in ["site", "location"]:
            info = dev.get(field)
            if isinstance(info, dict):
                entry[field] = _get_id(info)
        processed.append(entry)
    return processed


def _process_vm(vms: List[Dict]) -> List[Dict]:
    processed = []
    for vm in vms:
        vm_id = _get_id(vm)
        if not vm_id:
            continue
        disks = vm.get("virtualdisks", [])
        disk_ids = _extract_simple_ids(disks)
        processed.append({"id": vm_id, "vdisk": disk_ids})
    return processed


def _find_matching_clusters(devices: List[Dict], clusters: List[Dict]) -> Set[str]:
    cluster_map = {
        c.get("name", "n/a").lower(): c.get("id") for c in clusters if c.get("name")
    }
    matched_ids = set()
    for dev in devices:
        name = dev.get("name", "").lower()
        if name in cluster_map:
            c_id = cluster_map[name]
            if c_id is not None:
                log.debug(f"Matching cluster found for device '{name}': ID {c_id}")
                matched_ids.add(str(c_id))
    return matched_ids


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
