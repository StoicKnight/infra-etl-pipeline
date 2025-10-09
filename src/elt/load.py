import logging
from pathlib import Path
from typing import Dict, List

from src.utils.csv import write_csv

log = logging.getLogger(__name__)


def generate_report_stdout(
    source_file_name: str,
    updatable: List[Dict[str, str]],
    higher_version: List[Dict[str, str]],
    unresponsive: List[str],
) -> None:
    header = f"--- Report for {source_file_name} ---"
    print(f"\n{header}")

    print(f"\nFound {len(updatable)} minions that need an update:")
    for minion in updatable:
        print(f"  - {minion}")

    print(f"\nFound {len(higher_version)} minions with a higher version:")
    for minion in higher_version:
        print(f"  - {minion}")

    print(f"\nFound {len(unresponsive)} unresponsive minions:")
    for minion_id in unresponsive:
        print(f"  - {minion_id}")
    print("-" * len(header))


def export_report_to_csv(
    source_file_name: str,
    updatable: List[Dict[str, str]],
    higher_version: List[Dict[str, str]],
    unresponsive: List[str],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_filename = Path(source_file_name).stem + "_report.csv"
    csv_filepath = output_dir / csv_filename

    header = ["minion_id", "installed_version", "status"]
    rows = []

    for minion in updatable:
        minion_id, version = list(minion.items())[0]
        rows.append([minion_id, version, "Needs Update"])

    for minion in higher_version:
        minion_id, version = list(minion.items())[0]
        rows.append([minion_id, version, "Higher Version"])

    for minion_id in unresponsive:
        rows.append([minion_id, "N/A", "Unresponsive"])

    try:
        write_csv(csv_filepath, header, rows)
    except Exception as e:
        log.error(f"Unhandled exceprion exporting report to csv: {e}")
