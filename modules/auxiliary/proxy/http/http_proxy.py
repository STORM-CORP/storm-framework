import subprocess
import sys
import os
import smf

from rootmap import ROOT
from lib.roar.callbin.calling import call_bin

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
    bin = call_bin("http_prox")

    if not bin:
        smf.printf("[!] Binary not found =>", bin)
        return
        
    cmd = [bin]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    try:
        for line in process.stdout:
            smf.printf(line, file=sys.stdout, flush=True, end="")

    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        smf.printf("[*] Proxy successfully stopped.")
