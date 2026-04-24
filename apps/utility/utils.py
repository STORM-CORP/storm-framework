import os
import sys
import smf
import importlib

from typing import List
from rootmap import ROOT
from lib.roar.cache import cache_modules as cache

# utils.py It all contains help logic to make it easier during repairs and updates.
# This is included in the core category which cannot be modified.


# LOGIC GLOBAL WORDLIST
def resolve_path(kata_kunci):
    if not kata_kunci:
        return None
    assets_dir = os.path.join(ROOT, "assets/wordlist")

    # Check manual input first
    if os.path.exists(kata_kunci):
        return os.path.abspath(kata_kunci)

    # Search in assets
    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                if kata_kunci.lower() in file.lower():
                    return os.path.join(root, file)
    return None


# LOGIC USE
def load_module_dynamically(module_name):
    base_path = os.path.join(ROOT, "modules")
    normalized_input = module_name.strip().replace("\\", "/")

    if "." in normalized_input:
        raise ValueError("Gunakan '/' untuk path, bukan '.'")

    is_path_mode = "/" in normalized_input
    matches = []

    for root, dirs, files in os.walk(base_path):
        for file in files:
            name_without_ext, ext = os.path.splitext(file)
            if ext != ".py":
                continue

            full_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_file_path, ROOT)

            clean_path = (
                relative_path[:-3] if relative_path.endswith(".py") else relative_path
            )
            clean_path_norm = clean_path.replace(os.sep, "/")

            if not is_path_mode:
                if name_without_ext == normalized_input:
                    matches.append(clean_path_norm)
            else:
                if clean_path_norm == normalized_input or clean_path_norm.endswith(
                    "/" + normalized_input
                ):
                    matches.append(clean_path_norm)

    if not matches:
        return None

    if len(matches) > 1:
        return None

    module_dots = matches[0].replace("/", ".")

    try:
        return importlib.import_module(module_dots)
    except Exception as e:
        smf.printf(f"[-] ERROR UTILS =>", e, file=sys.stderr, flush=True)
        return None


# UI MODULES
EXT = (".py", ".go", ".rs", ".c", ".cpp", ".rb", ".php", ".sh", ".js", ".ts", ".html")


def count_modules():
    total = 0
    path = os.path.join(ROOT, "modules")
    if not os.path.exists(path):
        return 0

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(EXT) and file != "__init__.py":
                total += 1
    return total


def count_by_category():
    """
    Counting the number of modules based on category folders
    """
    stats = {}
    modules_path = os.path.join(ROOT, "modules")

    if not os.path.exists(modules_path):
        return stats

    # Take the folder directly under /modules (as the main category)
    categories = [
        d
        for d in os.listdir(modules_path)
        if os.path.isdir(os.path.join(modules_path, d))
    ]

    for cat in categories:
        cat_full_path = os.path.join(modules_path, cat)
        count = 0
        # Count files in the category folder (recursive)
        for root, dirs, files in os.walk(cat_full_path):
            for file in files:
                if file.endswith(EXT) and file != "__init__.py":
                    count += 1

        # Add to dictionary if the folder contains modules
        if count > 0:
            stats[cat] = count

    return stats


# LOGIC SHOW
def get_categories():
    """Get a list of category folders inside /modules"""
    modules_path = os.path.join(ROOT, "modules")
    if not os.path.exists(modules_path):
        return []
    return [
        d
        for d in os.listdir(modules_path)
        if os.path.isdir(os.path.join(modules_path, d)) and d != "__pycache__"
    ]


def get_modules_in_category(category: str) -> List[str]:
    """Retrieves all .py files within a specified category"""

    return cache.execute(category)
