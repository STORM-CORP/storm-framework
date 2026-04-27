import subprocess
import os
import sys
import smf
from rootmap import ROOT


def run_verif():
    lib = "external/source/out/core/integrity/verified"
    if not os.path.exists(lib):
        smf.printd("Binary verification missing", lib, level="CRITICAL")
        smf.printf("[!] ERROR => Rust binary not found in", lib)
        sys.exit(1)
    smf.printf("[∆] [INTEGRITY STORM RUNNING] [∆]")
    try:
        result = subprocess.run([lib])

        if result.returncode != 0:
            smf.printf("\n[-] CRITICAL => Reinstall Storm for security.)")
            smf.printd("Binary verification", result, level="CRITICAL")
            sys.exit(result.returncode)

        return True
    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printd("INTEGRITY VERIFICATION", e, level="CRITICAL")
        smf.printf("[!] ERROR =>", e, file=sys.stderr, flush=True)
        sys.exit(1)


def validate_binary_files():
    # Path to bin folder
    smf_dir = os.path.join(ROOT, "external", "source", "out")
    bin_name = ["libsigned.so", "verified"]

    found_map = {name: False for name in bin_name}
    failed = False

    # Loop to find binary
    for root, dirs, files in os.walk(smf_dir):
        for file in files:
            if file in found_map:
                found_map[file] = True

        if all(found_map.values()):
            break

    # Binary check loop
    for file_name, is_found in found_map.items():
        if not is_found:
            smf.printd("BINARY CORE MISSING", file_name, level="CRITICAL")
            smf.printf("[!] Binary core missing =>", file_name)
            failed = True

    return failed


def validate_binary_core():
    # Path to root
    bin_dir = os.path.abspath(ROOT)
    bin_names = ["smf.so"]

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
            smf.printd("BINARY CORE MISSING", file_name, level="CRITICAL")
            smf.printf("[!] Binary core missing =>", file_name)
            failed = True

    return failed


def check_critical_files():
    error = False

    if validate_binary_core():
        error = True

    if validate_binary_files():
        error = True

    if not os.path.exists(".env"):
        smf.printd("FILES KEY MISSING", ".env", level="CRITICAL")
        smf.printf("[!] CRITICAL => Integrity Key (.env) is missing!")
        smf.printf(
            "[*] Storm cannot verify the database signature without your unique keys."
        )
        smf.printf(
            "[*] Please run the installation/recovery script to regenerate your keys."
        )
        error = True

    if error:
        sys.exit(1)
