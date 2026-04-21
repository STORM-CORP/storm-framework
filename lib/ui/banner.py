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
        smf.printf("IMPORT BANNER ERROR =>", d, file=sys.stderr, flush=True)
        smf.printd("IMPORT BANNER ERROR", d, level="INFO")
        return

    except Exception as e:
        smf.printf("ERROR BANNER =>", e, file=sys.stderr, flush=True)
        smf.printd("ERROR BANNER EXCEPTION", e, level="MEDIUM")
        return
