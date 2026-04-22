# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import CC
from lib.roar.plugin.manager import PluginManager


def execute(args, context):
    plugin = PluginManager()

    if not args:
        smf.printf(
            f"{CC.RED}[!] ERROR => Invalid syntax. Run help to see the correct command.{CC.RESET}"
        )
        return context

    cmd = args[0].lower
    plugin.load(cmd)

    return context
