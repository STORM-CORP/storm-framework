import os
import subprocess

from rootmap import ROOT
from app.utility.spin import StormSpin
from scripts.cpl.advcore import safe_mode


def start_build():
    os.chdir(ROOT)
    cores = safe_mode()
    print("[*] Storm Run compilation...")

    with StormSpin:
        cmd = ["make", f"-j{cores}"]
        try:
            # Menjalankan Master Makefile
            # -j$(nproc) akan otomatis menggunakan semua core CPU kamu agar sangat cepat
            subprocess.run(cmd, check=True, capture_output=True)
            print("[✓] Storm Compilation successful")
        except subprocess.CalledProcessError as e:
            print(f"[!] Build failed => {e.stderr.decode()}")
        except FileNotFoundError:
            print("[!] make > not found. Please install build-essential.")


if __name__ == "__main__":
    start_build()
