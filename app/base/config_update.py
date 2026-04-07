import requests
import re
from version import VERSION
from app.utility.colors import C


def check_update():
    url = (
        "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/version.py"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', response.text)

        if match:
            latest = match.group(1)

            remote_v = tuple(map(int, latest.split(".")))
            local_v = tuple(map(int, VERSION.split(".")))

            if remote_v > local_v:
                print(f"{C.SUCCESS}[!] Current version => v{VERSION}")
                print(f"{C.SUCCESS}[!] Update available => v{latest}")
                print(f"{C.SUCCESS}[-] Type => storm update")
                print()
    except:
        pass
