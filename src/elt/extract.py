import json
from pathlib import Path
from typing import Any, Dict, List


def load_json_file(file_path: Path) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {file_path}: {e}")
        return {}


def extract_data_from_files(file_paths: List[Path]) -> List[Dict[str, Any]]:
    return list(map(load_json_file, file_paths))
