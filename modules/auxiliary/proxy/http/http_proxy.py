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
    lib = os.path.join(ROOT, "external", "source", "out")
    out = os.path.join(lib, "mod", "aux", "proxy", "http")
    bin = os.path.join(out, "http_prox")

    cmd = [bin]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    try:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        print("[*] Proxy successfully stopped.")
