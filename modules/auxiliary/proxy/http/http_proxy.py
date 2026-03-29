import subprocess
import sys
import os

from rootmap import ROOT

MOD_INFO = {
    "Name": "Forward proxy http",
    "Description": """
Perform surveillance on http traffic
read the header and body in full using
forward proxy logic.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Proxy", {"Description": "Reading headers and bodies"}],
    ],
    "DefaultAction": "Forward Proxy",
    "License": "SMF License",
}


def execute(options):
    lib = os.path.join(ROOT, "external", "source", "binary", "http_prox")

    try:
        # Run binary Go
        cmd = [lib]

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        return process
    except Exception as e:
        print(f"ERROR => {e}")


if __name__ == "__main__":
    process = execute()

    try:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        print("[*] Proxy berhasil dihentikan.")
