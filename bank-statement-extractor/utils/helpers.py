import os
import json
import json
from pathlib import Path
from pathlib import Path
from typing import Any, Dict
from typing import Any, Dict


def ensure_directory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def save_json(data: Dict[str, Any], file_path: str) -> None:
    ensure_directory(Path(file_path).parent)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as f:
        return json.load(f)

def file_exists(file_path: str) -> bool:
    return Path(file_path).exists()

def get_file_size(file_path: str) -> int:
    return Path(file_path).stat().st_size

def get_file_extension(file_path: str) -> str:
    return Path(file_path).suffix.lower()

def clean_filename(filename: str) -> str:
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename.strip()
