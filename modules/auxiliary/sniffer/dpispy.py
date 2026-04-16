import subprocess
import os
import smf

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

    bindir = os.path.join(ROOT, "external", "source", "out")
    out = os.path.join(bindir, "mod", "aux", "sniff")
    bin_path = os.path.join(out, "dpi_netspy")

    if not os.path.isfile(bin_path):
        smf.printf(f"[!] ERROR: Binary not found {bin_path}.")
        return False
    smf.printf(f"[*] Run Go-Sniffer on interface: {iface}")

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
            smf.printf(line.strip())

    except KeyboardInterrupt:
        proc.terminate()
    except Exception as e:
        smf.printf(f"[!] ERROR =>", e)

    return True
