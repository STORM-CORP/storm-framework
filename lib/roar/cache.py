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

        smf.printd(f"Initializing StormSmartCache at {self.db_path}", level="INFO")

        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()

            self.cursor.execute("PRAGMA journal_mode=WAL;")
            self.cursor.execute("PRAGMA synchronous=NORMAL;")
            smf.printd("SQLite Pragmas set to WAL and NORMAL", level="DEBUG")

            self._init_db()
        except Exception as e:
            smf.printd("Failed to connect or configure SQLite database", e, level="CRITICAL")
            raise

    def _init_db(self):
        smf.printd("Verifying module_cache schema and indexes", level="DEBUG")
        try:
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
            smf.printd("Schema validation completed", level="DEBUG")
        except Exception as e:
            smf.printd("Failed to initialize database schema", e, level="ERROR")
            raise

    def _fast_scan(
        self,
        directory: str,
        db_state: Dict[str, float],
        current_disk_files: Set[str],
        to_upsert: List[Tuple[str, float, str, str]],
    ):
        smf.printd(f"Scanning directory: {directory}", level="DEBUG")
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
                                    module_name.split("/")[0]
                                    if "/" in module_name
                                    else module_name
                                )

                                to_upsert.append(
                                    (full_path, mtime, category, module_name)
                                )
                                smf.printd(f"Module staged for upsert: {module_name}", level="INFO")
                            else:
                                smf.printd(f"File unchanged, skipping: {entry.name}", level="DEBUG")

        except PermissionError as e:
            smf.printd(f"Permission denied accessing directory: {directory}", e, level="WARN")
        except Exception as e:
            smf.printd(f"Unexpected error while scanning directory: {directory}", e, level="ERROR")

    def sync_modules(self) -> None:
        """Synchronize the disk with the cache database."""
        smf.printd("Starting module synchronization routine", level="INFO")
        try:
            self.cursor.execute("SELECT path, mtime FROM module_cache")
            db_state = {row[0]: row[1] for row in self.cursor.fetchall()}
            smf.printd(f"Loaded {len(db_state)} existing states from DB", level="DEBUG")

            current_disk_files: Set[str] = set()
            to_upsert: List[Tuple[str, float, str, str]] = []

            # Start scan from root folder modules
            self._fast_scan(self.modules_dir, db_state, current_disk_files, to_upsert)

            deleted_files = set(db_state.keys()) - current_disk_files

            if to_upsert or deleted_files:
                smf.printd(f"Delta detected -> Upsert: {len(to_upsert)}, Delete: {len(deleted_files)}", level="INFO")
                with self.conn:
                    if to_upsert:
                        self.cursor.executemany(
                            "INSERT OR REPLACE INTO module_cache (path, mtime, category, module_name) VALUES (?, ?, ?, ?)",
                            to_upsert,
                        )
                        smf.printd("Upsert transaction committed", level="DEBUG")

                    if deleted_files:
                        delete_payload = [(path,) for path in deleted_files]
                        self.cursor.executemany(
                            "DELETE FROM module_cache WHERE path = ?", delete_payload
                        )
                        smf.printd("Delete transaction committed", level="DEBUG")
            else:
                smf.printd("No drift detected between disk and database. Sync skipped.", level="INFO")
                
        except Exception as e:
            smf.printd("Fatal error during module synchronization", e, level="CRITICAL")

    def execute(self, category: str) -> List[str]:
        """
        An API to replace legacy functionality.
        It's very fast because it uses SQL Indexes and doesn't involve disk I/O.
        """
        smf.printd(f"Executing category fetch for: {category}", level="DEBUG")
        try:
            self.cursor.execute(
                "SELECT module_name FROM module_cache WHERE category = ?", (category,)
            )
            # Fetchall returns a list of tuples: [('exploits/test',), ('exploits/demo',)]
            results = [row[0] for row in self.cursor.fetchall()]
            smf.printd(f"Query returned {len(results)} records for category '{category}'", level="INFO")
            return results
        except Exception as e:
            smf.printd(f"Failed to execute lookup for category: {category}", e, level="ERROR")
            return []


# Global register
smf.printd("Allocating StormSmartCache global instance", level="DEBUG")
cache_modules = StormSmartCache()
                        
