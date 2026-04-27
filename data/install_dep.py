# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import json
import os
import subprocess
import sys

from rootmap import ROOT

def bootstrap():
    json_path = os.path.join(root_dir, 'data_storm.json')

    if not os.path.exists(json_path):
        print(f"[!] Configuration missing: {json_path}")
        return

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            # key: nama_import, value: nama_paket_pip
            libs = data.get("dependencies", {})
    except Exception as e:
        print(f"[!] Error reading dependencies: {e}")
        sys.exit(1)

    for import_name, package_name in libs.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"[*] Module '{import_name}' not found. Installing '{package_name}'...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package_name
                ])
                print(f"[+] Successfully installed {package_name}")
            except subprocess.CalledProcessError:
                print(f"[!] Failed to install {package_name}. Manual intervention required.")
                sys.exit(1)

if __name__ == "__main__":
    bootstrap()
