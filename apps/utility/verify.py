import subprocess
import os
import sys
from apps.utility.colors import C


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
        sys.exit(1)
