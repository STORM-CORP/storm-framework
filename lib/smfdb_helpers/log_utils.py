import sqlite3
import datetime
import rootmap
import smf

from pathlib import Path


def extract_logs(level_target: str, output_file: str = "log.txt"):
    """
    Extract logs from internal SQLite database by level.
    """

    db_dir = Path(rootmap.ROOT) / "lib" / "sqlite" / "logging"
    db_path = db_dir / "log.db"

    if not db_path.exists():
        smf.printf("[!] Database not found =>", db_path)
        return

    # Input Level Normalization
    level_query = level_target.strip().upper()

    try:
        # Open connection to SQLite (Read-Only Mode is safer)
        uri_path = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri_path, uri=True)
        cursor = conn.cursor()

        # Advanced SQL Queries (Take from the most recent)
        query = """
            SELECT timestamp, level, label, payload, caller_info 
            FROM system_logs 
            WHERE level = ? 
            ORDER BY timestamp DESC
        """
        cursor.execute(query, (level_query,))
        rows = cursor.fetchall()
        conn.close()

        # Validation if data is empty
        if not rows:
            smf.printf("[!] No log level =>", level_query)
            return

        home_dir = Path.home()
        dump_folder = home_dir / "storm_logs"
        dump_folder.mkdir(exist_ok=True)
        final_output_path = dump_folder / output_file

        # Write to file I/O
        with open(final_output_path, "w", encoding="utf-8") as f:
            # Report Header
            f.write("=" * 60 + "\n")
            f.write("  STORM FRAMEWORK - DIAGNOSTIC LOG REPORT\n")
            f.write(f"  Level        : {level_query}\n")
            f.write(f"  Total Entry  : {len(rows)} data\n")
            f.write(
                f"  Generated At : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("=" * 60 + "\n\n")

            # Data Iteration
            for row in rows:
                ts, lvl, label, payload, caller = row

                # Convert f64 Unix Epoch to common Date Format
                dt_str = datetime.datetime.fromtimestamp(ts).strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3]

                # Writing format like server log
                f.write(f"[{dt_str}] [{lvl}] <{caller}>\n")
                f.write(f" LABEL   : {label}\n")

                # If the payload contains any content, display it. Otherwise, ignore it.
                if payload:
                    f.write(f" PAYLOAD : {payload}\n")

                f.write("-" * 60 + "\n")

        smf.printd("System log extracted by user", final_output_path, level="INFO")
        smf.printf(f"[✓] Extraction Successful! {len(rows)} log lines =>", level_query)
        smf.printf("[!] File saved to =>", final_output_path)

    except sqlite3.Error as e:
        smf.printf(f"[-] A Database Log I/O error occurred")
        smf.printd("A Database Log I/O error occurred", e, level="ERROR")
    except Exception as e:
        smf.printf(f"[-] Extraction failure occurred")
        smf.printd("Extraction failure occurred", e, level="ERROR")
