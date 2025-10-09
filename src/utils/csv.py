import csv
import logging
from typing import List

log = logging.getLogger(__name__)


def write_csv(file_path: str, header: List, rows: List[List]):
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)
        log.info(f"Successfully exported report to {file_path}")
    except IOError as e:
        log.error(f"Error writing to CSV file {file_path}: {e}")
    except Exception as e:
        log.error(f"Unhandled exception writting to CSV file: {e}")
