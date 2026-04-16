import requests
import sys
import smf
from apps.utility.colors import C

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
SUBDOMAINS = [
    "www",
    "dev",
    "api",
    "mail",
    "blog",
    "test",
    "staging",
    "admin",
    "ftp",
    "vpn",
    "server",
    "cms",
    "cdn",
    "static",
    "app",
    "auth",
    "assets",
    "img",
    "images",
    "media",
    "beta",
    "demo",
    "panel",
    "dashboard",
    "internal",
    "intranet",
    "ssh",
    "git",
    "gitlab",
    "repo",
    "status",
    "cpanel",
    "webmail",
    "cpcalendars",
]

REQUIRED_OPTIONS = {"DOMAIN": ""}


def execute(options):
    """Searching for active subdomains"""
    target_domain = options.get("DOMAIN")

    target_domain = (
        target_domain.replace("http://", "").replace("https://", "").strip("/")
    )
    smf.printf(f"{C.HEADER} SUBDOMAIN ENUMERATION for {target_domain}")

    found_count = 0
    PROTOCOLS = ["http", "https"]
    for subdomain in SUBDOMAINS:
        for proto in PROTOCOLS:
            url = f"{proto}://{subdomain}.{target_domain}"
            try:
                response = requests.head(url, timeout=3, allow_redirects=True)
                status_code = response.status_code
                if status_code < 400 or status_code == 403:
                    smf.printf(
                        f"{C.SUCCESS}[✓] Subdomain Found: {url} - Status: {status_code}"
                    )
                    found_count += 1
            except KeyboardInterrupt:
                return
            except requests.exceptions.RequestException:
                pass
            except Exception as e:
                smf.printf(f"{C.ERROR}[!] ERROR on {url} =>", e, file=sys.stderr, flush=True)
                continue

    smf.printf(f"{C.SUCCESS}\n[✓] Subdomain active: {found_count}")
    if found_count == 0:
        smf.printf(f"{C.ERROR} No active subdomains found with list: {found_count}")
