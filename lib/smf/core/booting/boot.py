# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import sys
import time

from apps.utility.verify import *
from apps.utility.colors import C
from plugin.caching.utils_cache import StormSmartCache


def boot():
    # Smart Cache func call
    sync = StormSmartCache()
    # Check core startup security
    check_critical_files()
    # Verify file integrity
    run_verif()
    # sync cache modules
    sync.sync_modules()

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
