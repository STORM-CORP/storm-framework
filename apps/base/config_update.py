import requests
import json
import os
from apps.utility.colors import C
from rootmap import ROOT


def check_update():
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/data/data_version.json"
    try:
        latest_version = requests.get(url).json()["version"]
        data = os.path.join(ROOT, "data", "data_version.json")
        with open(data) as f:
            VERSION = json.load(f)["version"]

        if latest_version > VERSION:
            print(f"{C.SUCCESS}[!] Current version => v{VERSION}")
            print(f"{C.SUCCESS}[!] Update available => v{latest_version}")
            print(f"{C.SUCCESS}[-] Type => storm update")
            print()
    except Exception as e:
        print(f"ERROR CHECK UPDATE => {e}")
