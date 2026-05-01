# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import sqlite3
import smf
from pathlib import Path
from rootmap import ROOT

_BASE_DIR = Path(ROOT).resolve()
_DB_PATH = _BASE_DIR / "lib" / "sqlite" / "cached" / "cache.db"


def _get_db_connection() -> sqlite3.Connection:
    """Manage connections and initialize SQLite database schemas."""
    if not _DB_PATH.parent.exists():
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        smf.printd(
            f"The cache.db directory is created on {_DB_PATH.parent}", level="INFO"
        )

    conn = sqlite3.connect(_DB_PATH)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS binary_cache (
                name TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                category TEXT,
                last_mtime REAL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bin_name ON binary_cache(name)")
    except sqlite3.Error as e:
        smf.printd("Failed to initialize SQLite cache schema", e, level="CRITICAL")
        raise

    return conn


def sync_bin() -> None:
    """
    Scans the filesystem and synchronizes the binary paths to cache.db
    """
    smf.printd("Starting binary cache synchronization scan...", level="INFO")
    search_targets = {
        "module": _BASE_DIR / "external" / "source" / "out" / "module",
        "core": _BASE_DIR / "external" / "source" / "out" / "core",
    }

    found_on_disk = {}

    for cat, folder in search_targets.items():
        if not folder.exists():
            smf.printd(f"Target directory not found and skipped", folder, level="WARN")
            continue

        # rglob("*") Recursive search
        for entry in folder.rglob("*"):
            # Linux Validation: File is regular and has X_OK (executable bit)
            if entry.is_file() and os.access(entry, os.X_OK):
                found_on_disk[entry.name] = {
                    "path": str(entry.absolute()),
                    "category": cat,
                    "mtime": entry.stat().st_mtime,
                }
                smf.printd(f"Binary extracted: {entry.name} ({cat})", level="DEBUG")

    # Atomic SQLite Transactions (UPSERT Logic)
    try:
        with _get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete stale data (files deleted from the filesystem)
            cursor.execute("SELECT name FROM binary_cache")
            cached_names = {row[0] for row in cursor.fetchall()}

            removed = [(name,) for name in cached_names if name not in found_on_disk]
            if removed:
                cursor.executemany("DELETE FROM binary_cache WHERE name = ?", removed)
                smf.printd(
                    f"Clean {len(removed)} binary that is no longer present in the cache.",
                    level="INFO",
                )

            # Insert or Update (based on mtime)
            updated_count = 0
            for name, data in found_on_disk.items():
                cursor.execute(
                    """
                    INSERT INTO binary_cache (name, path, category, last_mtime)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        path = excluded.path,
                        last_mtime = excluded.last_mtime,
                        category = excluded.category
                    WHERE last_mtime != excluded.last_mtime
                """,
                    (name, data["path"], data["category"], data["mtime"]),
                )

                if cursor.rowcount > 0:
                    updated_count += 1

            conn.commit()

            smf.printd(
                f"DB sync complete. Total: {len(found_on_disk)} binary, Updated/Inserted:",
                updated_count,
                level="INFO",
            )

    except sqlite3.Error as e:
        smf.printd(
            f"An I/O error occurred during the DB sync transaction.", e, level="ERROR"
        )


def call_bin(binary_name: str) -> str:
    """
    Gets the absolute path of the binary.
    Lookup complexity is O(1) because it uses PRIMARY KEY index in SQLite.
    """
    smf.printd(
        f"Caller makes a path resolution request for", binary_name, level="DEBUG"
    )

    try:
        with _get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT path FROM binary_cache WHERE name = ?", (binary_name,)
            )
            row = cursor.fetchone()

        if not row:
            smf.printd(
                f"Resolution failed: Binary not recorded in the database.",
                binary_name,
                level="ERROR",
            )
            # Exception dilempar agar caller module bisa memberikan error handling spesifik
            raise FileNotFoundError(f"Binary {binary_name} not found.")

        smf.printd(f"Successful resolution: {binary_name} -> {row[0]}", level="DEBUG")
        return row[0]

    except sqlite3.Error as e:
        smf.printd("Database interaction error while lookup path", e, level="CRITICAL")
        raise
