import os
import subprocess
import threading
import smf
from rootmap import ROOT

MOD_INFO = {
    "Name": "Searching for subdomains",
    "Description": """
Perform a scan on the specified subdomain
to search and find subdomains that allow for
exploited.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Scanner", {"Description": "Searching for sensitive subdomains"}],
    ],
    "DefaultAction": "Scanner",
    "License": "SMF License",
}
REQUIRED_OPTIONS = {"DOMAIN": "", "SUBDOM": "", "THREAD": ""}


def execute(options):
    target_domain = options.get("DOMAIN")
    wordlist_path = options.get("SUBDOM")
    threads = str(options.get("THREAD"))

    bin_path = os.path.join(ROOT, "external", "source", "out", "recon", "subenum")

    if not os.path.exists(bin_path):
        smf.printf(f"[!] ERROR => Binary not found at >", bin_path)
        return

    smf.printf(f"\n[*] Starting SUBDOMAIN ENUMERATION for", target_domain)
    smf.printf()

    cmd = [bin_path, "-d", target_domain, "-w", wordlist_path, "-c", threads]

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )

        # Thread untuk parsing hasil valid (stdout)
        def read_stdout(pipe):
            for line in iter(pipe.readline, ""):
                if line:
                    smf.printf(f"[✓] {line.strip()}")
            pipe.close()

        # Thread untuk parsing info/error (stderr)
        def read_stderr(pipe):
            for line in iter(pipe.readline, ""):
                if line:
                    smf.printf(f"{line.strip()}")
            pipe.close()

        stdout_thread = threading.Thread(target=read_stdout, args=(process.stdout,))
        stderr_thread = threading.Thread(target=read_stderr, args=(process.stderr,))

        stdout_thread.start()
        stderr_thread.start()

        process.wait()
        stdout_thread.join()
        stderr_thread.join()

    except Exception as e:
        smf.printf(f"[!] An IPC module error occurred")
        smf.printd("Subenum IPC error", e, level="ERROR")
