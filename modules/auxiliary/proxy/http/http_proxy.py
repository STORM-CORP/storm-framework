import subprocess
import sys
import os

from rootmap import ROOT

MOD_INFO = {
    "Name": "Forward proxy http",
    "Description": """
Melakukan pengintaian terhadap trafik http
membaca header dan body secara lengkap menggunakan
logika fordward proxy.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Proxy", {"Description": "Baca header dan body"}],
    ],
    "DefaultAction": "forward proxy",
    "License": "SMF License",
}

def execute(options=None):
    lib = os.path.join(ROOT, "external", "source", "binary", "http_prox")

    # Run binary Go
    cmd = [lib]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return process


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
