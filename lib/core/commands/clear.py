# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import smf
import apps.base.config_ui as ui
from apps.banners.uib import *
from lib.smf.core.console.engine import Context


# The clear command is used to clear the interface line history
# so that it looks clean like it was just opened without deleting previously used data.
###
# Tidiness is everything
def execute(args: list[str], ctx: Context) -> None:
    # Clean the screen according to the OS
    os.system("cls" if os.name == "nt" else "clear")
    # Redisplay tool identity
    smf.printf(banner_live())
    ui.stormUI()
