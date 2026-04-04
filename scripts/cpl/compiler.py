import os
import subprocess
from rootmap import ROOT
from app.utility.spin import StormSpin
from scripts.cpl.advcore import safe_mode


def start_build():
    os.chdir(ROOT)
    cores = safe_mode()

    # Path output mutlak
    bin_path = os.path.abspath(os.path.join(ROOT, "external/source/bin"))
    os.makedirs(bin_path, exist_ok=True)
    os.environ["BIN_DIR"] = bin_path

    # Daftar folder yang HARUS diabaikan
    ignore_dirs = {".git", "bin", "__pycache__", "node_modules", "cache", "vendor"}

    print("[*] Storm Run compilation...")
    with StormSpin():
        # Scan dari titik ROOT
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            if "Makefile" in files:
                if os.path.abspath(root) == os.path.abspath(ROOT):
                    continue

                try:
                    # Jalankan kompilasi di tiap folder modul
                    cmd = ["make", "-C", root, f"-j{cores}"]
                    subprocess.run(cmd, check=True, capture_output=True)
                    print("[✓] Storm Compilation successful")
                except subprocess.CalledProcessError as e:
                    module = os.path.basename(root)
                    print(f"[!] Build failed in {module} => {e.stderr.decode()}")
                except FileNotFoundError:
                    print("[!] make > not found. Please install build-essential.")
                    break


if __name__ == "__main__":
    start_build()
