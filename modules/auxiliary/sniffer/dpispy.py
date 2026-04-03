import subprocess
import os
from rootmap import ROOT

MOD_INFO = {
    "Name": "Deep Packet Inspection",
    "Description": """
Analyzing incoming and outgoing packets
to find out the origin of the packet,
payload content if HTTP, analyze connection
malware.
    """,
    "Author": ["zxelzy"],
    "Action": [
        ["DPI", {"Description": "Analyze Packet"}],
    ],
    "DefaultAction": "DPI",
    "License": "SMF License",
}
REQUIRED_OPTIONS = {
    "INTERFACE": "example: eth0",
}


def execute(options):
    iface = options.get("INTERFACE")

    bindir = os.path.join(ROOT, "external", "source", "bin")
    bin_path = os.path.join(bindir, "dpi_netspy")
    if not os.path.isfile(bin_path):
        print(f"[!] ERROR: Binary not found {bin_path}.")
        return False
    print(f"[*] Run Go-Sniffer on interface: {iface}")

    try:
        # Calling a Go binary with interface arguments
        proc = subprocess.Popen(
            [bin_path, iface],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        while True:
            line = proc.stdout.readline()
            if not line:
                break
            print(line.strip())

    except KeyboardInterrupt:
        proc.terminate()
    except Exception as e:
        print(f"[!] ERROR: {e}")

    return True
