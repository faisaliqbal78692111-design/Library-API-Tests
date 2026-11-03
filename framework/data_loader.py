import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "test-data"


def load_json(name: str):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def load_csv(name: str):
    with open(DATA_DIR / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
