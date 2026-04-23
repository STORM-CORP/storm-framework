# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import sqlite3
import smf

from typing import List, Set, Tuple, Dict
from rootmap import ROOT


class StormSmartCache:
    def __init__(self):
        self.db_path = os.path.join(ROOT, "lib", "sqlite", "cached", "cache.db")
        self.modules_dir = os.path.join(
            ROOT, "modules"
        )  # Base path for relative calculations
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("PRAGMA journal_mode=WAL;")
        self.cursor.execute("PRAGMA synchronous=NORMAL;")

        self._init_db()

    def _init_db(self):
        # NEW SCHEMA: Added category and module_name columns
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_cache (
                path TEXT PRIMARY KEY,
                mtime REAL,
                category TEXT,
                module_name TEXT
            )
        """)
        # OPTIMIZATION: Indexing on the category column so that the `show` command query
        #               executed in microseconds
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON module_cache(category)"
        )
        self.conn.commit()

    def _fast_scan(
        self,
        directory: str,
        db_state: Dict[str, float],
        current_disk_files: Set[str],
        to_upsert: List[Tuple[str, float, str, str]],
    ):
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        self._fast_scan(
                            entry.path, db_state, current_disk_files, to_upsert
                        )

                    elif entry.is_file(follow_symlinks=False):
                        # FILTERING: Apply filter logic to the orchestrator
                        if entry.name.endswith(".py") and entry.name != "__init__.py":
                            full_path = entry.path
                            current_disk_files.add(full_path)
                            mtime = entry.stat().st_mtime

                            if (
                                full_path not in db_state
                                or db_state[full_path] != mtime
                            ):
                                # METADATA CALCULATION FOR DATABASE
                                rel_path = os.path.relpath(full_path, self.modules_dir)
                                # In module_name format always use forward slash
                                # (standard framework)
                                module_name = rel_path.replace(os.sep, "/").replace(
                                    ".py", ""
                                )
                                category = (
                                    module_name.split("/")[-1]
                                )

                                to_upsert.append(
                                    (full_path, mtime, category, module_name)
                                )

        except PermissionError:
            smf.printf(f"[WARNING] Permission denied accessing: {directory}")

    def sync_modules(self) -> None:
        """Synchronize the disk with the cache database."""
        self.cursor.execute("SELECT path, mtime FROM module_cache")
        db_state = {row[0]: row[1] for row in self.cursor.fetchall()}

        current_disk_files: Set[str] = set()
        to_upsert: List[Tuple[str, float, str, str]] = []

        # Start scan from root folder modules
        self._fast_scan(self.modules_dir, db_state, current_disk_files, to_upsert)

        deleted_files = set(db_state.keys()) - current_disk_files

        if to_upsert or deleted_files:
            with self.conn:
                if to_upsert:
                    self.cursor.executemany(
                        "INSERT OR REPLACE INTO module_cache (path, mtime, category, module_name) VALUES (?, ?, ?, ?)",
                        to_upsert,
                    )

                if deleted_files:
                    delete_payload = [(path,) for path in deleted_files]
                    self.cursor.executemany(
                        "DELETE FROM module_cache WHERE path = ?", delete_payload
                    )

    def get_show_modules(self, category: str) -> List[str]:
        """
        An API to replace legacy functionality.
        It's very fast because it uses SQL Indexes and doesn't involve disk I/O.
        """
        self.cursor.execute(
            "SELECT module_name FROM module_cache WHERE category = ?", (category,)
        )
        # Fetchall returns a list of tuples: [('exploits/test',), ('exploits/demo',)]
        return [row[0] for row in self.cursor.fetchall()]
