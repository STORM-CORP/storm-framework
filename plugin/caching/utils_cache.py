# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import sqlite3
import smf

from typing import List, Set, Tuple, Dict
from rootmap import ROOT


class StormSmartCache:
    def __init__(self):
        self.db_path = os.path.join(
            ROOT, "lib", "smf", "core", "sf", "cache", "storm_cache.db"
        )
        self.modules_dir = os.path.join(
            ROOT, "modules"
        )  # Base path untuk kalkulasi relatif
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("PRAGMA journal_mode=WAL;")
        self.cursor.execute("PRAGMA synchronous=NORMAL;")

        self._init_db()

    def _init_db(self):
        # SKEMA BARU: Menambahkan kolom category dan module_name
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_cache (
                path TEXT PRIMARY KEY,
                mtime REAL,
                category TEXT,
                module_name TEXT
            )
        """)
        # OPTIMASI: Indexing pada kolom category agar query perintah `show`
        #           dieksekusi dalam hitungan mikrodetik
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
                        # FILTERING: Terapkan logika lama kamu di level scanner
                        if entry.name.endswith(".py") and entry.name != "__init__.py":
                            full_path = entry.path
                            current_disk_files.add(full_path)
                            mtime = entry.stat().st_mtime

                            if (
                                full_path not in db_state
                                or db_state[full_path] != mtime
                            ):
                                # KALKULASI METADATA UNTUK DATABASE
                                rel_path = os.path.relpath(full_path, self.modules_dir)
                                # Pastikan format module_name menggunakan forward slash
                                # (standar framework)
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

        except PermissionError:
            smf.printf(f"[WARNING] Permission denied accessing: {directory}")

    def sync_modules(self) -> None:
        """Melakukan sinkronisasi disk dengan database cache."""
        self.cursor.execute("SELECT path, mtime FROM module_cache")
        db_state = {row[0]: row[1] for row in self.cursor.fetchall()}

        current_disk_files: Set[str] = set()
        to_upsert: List[Tuple[str, float, str, str]] = []

        # Mulai scan dari root folder modules
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
        API untuk menggantikan fungsi lama.
        Sangat cepat karena menggunakan SQL Index dan tidak menyentuh disk I/O.
        """
        self.cursor.execute(
            "SELECT module_name FROM module_cache WHERE category = ?", (category,)
        )
        # Fetchall mengembalikan list of tuples: [('exploits/test',), ('exploits/demo',)]
        return [row[0] for row in self.cursor.fetchall()]
