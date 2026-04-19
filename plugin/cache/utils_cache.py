import os
import sqlite3
from rootmap import ROOT


class StormSmartScanner:
    def __init__(self):
        self.db = os.path.join(ROOT, "lib", "core", "sf", "cache", "storm_cache.db")
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_cache (
                path TEXT PRIMARY KEY,
                mtime REAL
            )
        """)
        self.conn.commit()

    def sync_modules(self, target_dir):
        # 1. Ambil state saat ini dari Database (Cache)
        self.cursor.execute("SELECT path, mtime FROM module_cache")
        db_state = {row[0]: row[1] for row in self.cursor.fetchall()}

        current_disk_files = set()
        to_upsert = []  # List untuk Insert/Update

        # 2. Scanning Disk
        for root, _, files in os.walk(target_dir):
            for file in files:
                full_path = os.path.join(root, file)
                current_disk_files.add(full_path)

                # Cek metadata (mtime)
                mtime = os.path.getmtime(full_path)

                # Logika Pintar: Hanya proses jika file baru atau berubah
                if full_path not in db_state or db_state[full_path] != mtime:
                    to_upsert.append((full_path, mtime))
                    print(f"[NEW/MODIFIED] {file}")
                else:
                    # File sudah ada dan tidak berubah
                    pass

        # 3. Identifikasi file yang sudah dihapus secara fisik
        deleted_files = set(db_state.keys()) - current_disk_files

        # 4. Eksekusi Batch ke SQLite (Sangat Cepat dengan Transaction)
        if to_upsert or deleted_files:
            with self.conn:
                # Update atau Insert file baru/berubah
                self.cursor.executemany(
                    "INSERT OR REPLACE INTO module_cache (path, mtime) VALUES (?, ?)",
                    to_upsert,
                )

                # Hapus file yang sudah tidak ada di disk
                for path in deleted_files:
                    print(f"[REMOVED] {os.path.basename(path)}")
                    self.cursor.execute(
                        "DELETE FROM module_cache WHERE path = ?", (path,)
                    )

            print(
                f"Sync selesai: {len(to_upsert)} updated, {len(deleted_files)} removed."
            )
        else:
            print("Cache sudah up-to-date. Tidak ada I/O berat dilakukan.")

        return list(current_disk_files)


# Penggunaan di Storm Framework
scanner = StormSmartScanner()
all_modules = scanner.sync_modules("./modules")
