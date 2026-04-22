import smf

from apps.utility.colors import CC
from lib.roar.plugin.manager import PluginManager

def execute(args, context):

    plugin = PluginManager()
    cmd = args[0].lower
    
    if not cmd:
        smf.printf(
            f"{CC.YELLOW}[!] WARN => Invalid syntax. Usage: load <plugin_name>{CC.RESET}"
        )
        return context

    if cmd:
        plugin.load(cmd)

return context
