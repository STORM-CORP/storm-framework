import subprocess
import os
import sys

from apps.utility.colors import C
from rootmap import ROOT


def run_verif():
    lib = "external/source/bin/verified"
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


def validate_binary_files():
    # Path to bin folder
    bin_dir = os.path.join(ROOT, "external", "source", "bin")
    bin_names = ["signed.so", "verified"]

    found_map = {name: False for name in bin_names}
    failed = False

    # Loop to find binary
    for root, dirs, files in os.walk(bin_dir):
        for file in files:
            if file in found_map:
                found_map[file] = True

        if all(found_map.values()):
            break

    # Binary check loop
    for file_name, is_found in found_map.items():
        if not is_found:
            print(f"{C.ERROR}[!] Binary core missing => {file_name}{C.RESET}")
            failed = True

    return failed


def check_critical_files():
    error = False

    if validate_binary_files():
        error = True
        
    if not os.path.exists(".env"):
        print(f"{C.ERROR}[!] CRITICAL => Integrity Key (.env) is missing!{C.RESET}")
        print(
            f"[*] Storm cannot verify the database signature without your unique keys."
        )
        print(
            f"[*] Please run the installation/recovery script to regenerate your keys."
        )
        error = True
        
    if error:
        sys.exit(1)
