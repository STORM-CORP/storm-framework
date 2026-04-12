# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import sys
import time

from apps.utility.verify import *
from apps.utility.colors import C


def boot():
    check_critical_files()
    run_verif()
    try:
        for i in range(6, 0, -1):
            sys.stdout.write(
                f"\r{C.SUCCESS}[*] Verification Success! Start Storm: [{i}] {C.RESET}"
            )
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        return
