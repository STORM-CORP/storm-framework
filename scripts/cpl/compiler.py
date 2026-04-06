import os
import subprocess

from rootmap import ROOT
from app.utility.spin import StormSpin
from scripts.cpl.advcore import safe_mode


def start_build():
    os.chdir(ROOT)
    cores = safe_mode()

    # Cache is saved
    rust_cache = os.path.abspath(os.path.join(ROOT, "lib/smf/core/cache/rust-session"))
    os.makedirs(rust_cache, exist_ok=True)

    # Binary output is saved
    bin_path = os.path.abspath(os.path.join(ROOT, "external/source/bin"))
    os.makedirs(bin_path, exist_ok=True)

    # context to Makefile
    os.environ["CARGO_TARGET_DIR"] = rust_cache
    os.environ["BIN_DIR"] = bin_path

    # Ignore folder list
    ignore_dirs = {".git", "bin", "__pycache__", "node_modules", "cache", "vendor"}

    # Setup loading
    with StormSpin():
        # running loop
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            if "Makefile" in files:
                if os.path.abspath(root) == os.path.abspath(ROOT):
                    continue
                try:  # Running make
                    cmd = ["make", "-C", root, f"-j{cores}"]
                    subprocess.run(cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    module = os.path.basename(root)
                    print(f"[!] Build failed in {module} => {e.stderr.decode()}")
                except FileNotFoundError as e:
                    print(f"[!] Make => {e}")
                    break

    print("[✓] Compilation successful.")


if __name__ == "__main__":
    start_build()
