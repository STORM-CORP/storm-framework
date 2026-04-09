import subprocess
import os
import sys

from pathlib import Path
from apps.utility.colors import C
from rootmap import ROOT

def run_verif():
    lib = "external/source/bin/check"
    if not os.path.exists(lib):
        print(f"[-] ERROR => Rust binary not found in {lib}")
        sys.exit(1)
    print(f"[∆] [INTEGRITY STORM RUNNING] [∆]")
    try:
        result = subprocess.run([lib])

        if result.returncode != 0:
            print(f"\n[-] CRITICAL => Reinstall Storm for security.)")
            sys.exit(result.returncode)

        return True

    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"[-] ERROR => {e}")
        sys.exit(1)


def check_critical_files():
    if not os.path.exists(".env"):
        print(f"{C.ERROR}[!] CRITICAL => Integrity Key (.env) is missing!{C.RESET}")
        print(
            f"[*] Storm cannot verify the database signature without your unique keys."
        )
        print(
            f"[*] Please run the installation/recovery script to regenerate your keys."
        )
        
        validate_binary_files()
        sys.exit(1)


def validate_binary_files():
    """
    Checking core binaries required for startup
    """
    files_bin = ['signed.so', 'check']
    bin = os.path.join(ROOT, "external", "source", "bin")
    base_path = Path(bin)
    
    # Convert rglob generator to set for O(1) lookup efficiency
    # We only take the file name to match.
    found_files = {p.name for p in base_path.rglob('*') if p.is_file()}
    
    for file_name in files_bin:
        if file_name not in found_files:
            # Stop execution and throw an error
            raise FileNotFoundError(f"{C.ERROR}[!] CRITICAL => Binary core missing => {file_name}")
