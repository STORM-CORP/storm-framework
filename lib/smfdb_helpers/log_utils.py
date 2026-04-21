import sqlite3
import datetime
import rootmap
import smf

from pathlib import Path


def extract_logs(level_target: str, output_file: str = "log.txt"):
    """
    Mengekstrak log dari database SQLite internal berdasarkan level.
    Contoh: extract_logs("CRITICAL", "log_critical.txt")
    """

    # 1. Resolusi Path (Sama persis dengan arsitektur Rust kita)
    db_dir = Path(rootmap.ROOT) / "lib" / "sqlite" / "logging"
    db_path = db_dir / "log.db"

    if not db_path.exists():
        print(f"[-] Database not found => {db_path}")
        return

    # 2. Normalisasi Input Level
    # User mungkin mengetik "critical", "CRITICAL", atau " medium "
    level_query = level_target.strip().upper()

    # Mapping custom jika Anda punya level non-standar (opsional)
    if level_query == "MEDIUM":
        level_query = "WARN"  # Asumsi medium adalah Warning

    try:
        # 3. Buka koneksi ke SQLite (Mode Read-Only lebih aman)
        # URI mode mencegah kita tidak sengaja mengunci database jika sedang dipakai Rust
        uri_path = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri_path, uri=True)
        cursor = conn.cursor()

        # 4. Query SQL Tingkat Lanjut (Ambil dari yang paling baru)
        query = """
            SELECT timestamp, level, label, payload, caller_info 
            FROM system_logs 
            WHERE level = ? 
            ORDER BY timestamp DESC
        """
        cursor.execute(query, (level_query,))
        rows = cursor.fetchall()
        conn.close()

        # Validasi jika data kosong
        if not rows:
            smf.printf(f"[!] No log level =>", level_query)
            return

        # 5. Tulis ke file I/O
        with open(output_file, "w", encoding="utf-8") as f:
            # Header Laporan
            f.write("=" * 60 + "\n")
            f.write(f"  STORM FRAMEWORK - DIAGNOSTIC LOG REPORT\n")
            f.write(f"  Level        : {level_query}\n")
            f.write(f"  Total Entry  : {len(rows)} data\n")
            f.write(
                f"  Generated At : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("=" * 60 + "\n\n")

            # Iterasi Data
            for row in rows:
                ts, lvl, label, payload, caller = row

                # Konversi f64 Unix Epoch dari Rust ke Format Tanggal Manusia
                dt_str = datetime.datetime.fromtimestamp(ts).strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3]

                # Format penulisan seperti log server enterprise
                f.write(f"[{dt_str}] [{lvl}] <{caller}>\n")
                f.write(f" LABEL   : {label}\n")

                # Jika payload ada isinya, tampilkan. Jika tidak, abaikan.
                if payload:
                    f.write(f" PAYLOAD : {payload}\n")

                f.write("-" * 60 + "\n")

        smf.printf(
            f"[+] Extraction Successful! {len(rows)} log lines => {level_query} > saved to => {output_file}"
        )

    except sqlite3.Error as e:
        smf.printf(f"[-] A Database Log I/O error occurred")
        smf.printd("A Database Log I/O error occurred", e, level="INFO")
    except Exception as e:
        smf.printf(f"[-] Extraction failure occurred")
        smf.printd("Extraction failure occurred", e, level="HIGH")
