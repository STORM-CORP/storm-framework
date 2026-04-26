# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import sys
import time
import smf

from apps.utility.verify import *
from apps.utility.colors import C
from lib.roar.plugin_api import plugin
from lib.roar.cache import cache_modules as cache


def boot():
    smf.printd("Boot starting...", level="INFO")
    smf.printd("Start checking the core...", level="INFO")
    # Check core startup security
    check_critical_files()
    smf.printd("Check core success", level="INFO")
    # Boot Plugin Manager
    plugin.boot()
    smf.printd("Boot plugin successfuls", level="INFO")
    # Cache modules synchronization
    cache.sync_modules()
    smf.printd("Module synchronization successful", level="INFO")
    # Verify file integrity
    run_verif()
    smf.printd("Verification of integrity check success", level="INFO")
    # Countdown to pause and start
    try:
        for i in range(6, 0, -1):
            sys.stdout.write(
                f"\r{C.SUCCESS}[*] Verification Success! Start Storm: [{i}] {C.RESET}"
            )
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        return
