import os
import smf
import sys
import apps.base.config_ui as ui

from apps.base.config_update import *
from apps.banners.uib import banner_live


def banner():
    try:
        os.system("clear")
        print(banner_live())
        ui.stormUI()
        check_update()
    except ImportError as d:
        smf.printf(f"ERROR BANNER IMPORT =>", d, file=sys.stderr, flush=True)
        return

    except Exception as e:
        smf.printf(f"ERROR BANNER =>", e, file=sys.stderr, flush=True)
        return
