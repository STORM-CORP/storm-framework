import os
import subprocess
from rootmap import ROOT
from app.utility.spin import StormSpin
from scripts.cpl.advcore import safe_mode


def start_build():
    os.chdir(ROOT)
    cores = safe_mode()

    shared_rust_cache = os.path.abspath(
        os.path.join(ROOT, "lib/smf/core/cache/rust-session")
    )
    os.makedirs(shared_rust_cache, exist_ok=True)
    bin_path = os.path.abspath(os.path.join(ROOT, "external/source/bin"))
    os.makedirs(bin_path, exist_ok=True)

    # context to Makefile
    os.environ["CARGO_TARGET_DIR"] = shared_rust_cache
    os.environ["BIN_DIR"] = bin_path

    # Daftar folder yang HARUS diabaikan
    ignore_dirs = {".git", "bin", "__pycache__", "node_modules", "cache", "vendor"}
    with StormSpin():
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            if "Makefile" in files:
                if os.path.abspath(root) == os.path.abspath(ROOT):
                    continue
                try:
                    cmd = ["make", "-C", root, f"-j{cores}"]
                    subprocess.run(cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    module = os.path.basename(root)
                    print(f"[!] Build failed in {module} => {e.stderr.decode()}")
                except FileNotFoundError:
                    print("[!] make > not found. Please install build-essential.")
                    break
    print("[✓] Compilation successful.") 

if __name__ == "__main__":
    start_build()
