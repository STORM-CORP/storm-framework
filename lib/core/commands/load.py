# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import CC
from lib.roar.plugin.manager import PluginManager


def execute(args, context):
    cmd = args[0].lower
    plugin = PluginManager()

    if not cmd:
        smf.printf(
            f"{CC.RED}[!] ERROR => Invalid syntax. Run help to see the correct command.{CC.RESET}"
        )
        return context

    if cmd:
        plugin.load(cmd)
        
    return context
    
