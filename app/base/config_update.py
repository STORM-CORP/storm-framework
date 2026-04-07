import requests
import json
from app.utility.colors import C


def check_update():
    url = (
        "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/version.json"
    )
    try:
        latest_version = requests.get(url).json()['version']
        with open('version.json') as f:
            VERSION = json.load(f)['version']
    
        if latest_version > VERSION:
            print(f"{C.SUCCESS}[!] Current version => v{VERSION}")
            print(f"{C.SUCCESS}[!] Update available => v{latest_version}")
            print(f"{C.SUCCESS}[-] Type => storm update")
            print()
    except:
        pass
