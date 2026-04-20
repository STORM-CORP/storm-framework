import sys
import smf
import requests
import subprocess
from apps.utility.colors import C


def run_update():
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/data/data_version.json"
    try:
        latest_version = requests.get(url).json()["version"]
        
        smf.printd("Monitoring the version update retrieval process =>", url)
    except Exception as e:
        smf.printf("ERROR VERSION UPDATE =>", e)
        smf.printf("ERROR VERSION UPDATE =>", e)

    # 1. Get the latest info without changing the locale first
    subprocess.run(["git", "fetch", "--all"], stdout=subprocess.DEVNULL)

    # 2. CHECK CHANGES: Compare local (HEAD) with server (origin/main)
    check_diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "origin/main"],
        capture_output=True,
        text=True,
    )

    # 3. Reset Execution (Update file to the latest version)
    process = subprocess.run(
        ["git", "reset", "--hard", "origin/main"], stdout=subprocess.PIPE, text=True
    )

    if process.returncode == 0:
        smf.printf(
            f"{C.SUCCESS}\n[✓] System updated to version => {latest_version}{C.RESET}"
        )

    # 4. Trigger Compiler ONLY IF needed
    try:
        from scripts.cpl import compiler

        compiler.start_build()
        from external.source.out.core.integrity import libsigned 
        
        libsigned.storm_sign()

        return True
    except Exception as e:
        smf.printd("[!] ERROR UPDATE =>", e)
        smf.printf("[!] ERROR UPDATE =>", e)
        return False
