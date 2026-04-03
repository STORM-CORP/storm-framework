import os
import app.base.config_ui as ui

from app.banners.uib import banner


def execute(args, context):
    # Clean the screen according to the OS
    os.system("cls" if os.name == "nt" else "clear")
    # Redisplay tool identity
    print(banner())
    ui.stormUI()
    return context
