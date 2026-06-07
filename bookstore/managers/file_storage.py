"""
file_storage.py — Shared JSON persistence helper.

All manager classes (UserManager, CatalogueManager, OrderManager) use this
module to load and save their data files. Follows the Information Expert
heuristic: storage logic is centralised here rather than duplicated across
managers.

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _path(filename):
    """Resolve a filename to its full path inside the data directory."""
    return os.path.join(DATA_DIR, filename)


def load(filename):
    """Load a JSON file and return its contents as a list. Returns [] if missing."""
    filepath = _path(filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save(filename, data):
    """Save a list to a JSON file, creating the data directory if needed."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = _path(filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_dict(filename):
    """Load a JSON file that contains a dict. Returns {} if missing."""
    filepath = _path(filename)
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dict(filename, data):
    """Save a dict to a JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = _path(filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
