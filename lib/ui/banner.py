import os
import apps.base.config_ui as ui

from apps.base.config_update import *
from apps.banners.uib import banner


def banner():
    os.system("clear")
    print(banner())
    ui.stormUI()
    check_update()
