from typing import Tuple


def parse_version_string(version_str: str) -> Tuple[int, int]:
    try:
        parts = version_str.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        return major, minor
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid version string format: {version_str}") from e
