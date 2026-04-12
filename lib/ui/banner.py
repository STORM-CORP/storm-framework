import os
import apps.base.config_ui as ui

from apps.base.config_update import *
from apps.banners.uib import banner


def banner():
    try:
        os.system("clear")
        print(banner())
        ui.stormUI()
        check_update()
    except ImportError as d:
        print(f"ERROR BANNER IMPORT => {d}")
        return

    except Exception as e:
        print(f"ERROR BANNER => {e}")
        return
