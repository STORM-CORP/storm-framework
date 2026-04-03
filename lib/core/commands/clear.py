# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import app.base.config_ui as ui
from app.banners.uib import banner


# The clear command is used to clear the interface line history
# so that it looks clean like it was just opened without deleting previously used data.
###
# Tidiness is everything
def execute(args, context):
    # Clean the screen according to the OS
    os.system("cls" if os.name == "nt" else "clear")
    # Redisplay tool identity
    print(banner())
    ui.stormUI()
    return context
