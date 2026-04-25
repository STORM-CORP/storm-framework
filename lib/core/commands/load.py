# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import *
from lib.smf.core.console.engine import Context


# This command is used to activate the plugin.
# by loading it into memory manually
# so that it can be immediately activated and used by the machine.
#
# Command => load <plugin_name>
#
# It will automatically load the plugin into memory.
def execute(args: list[str], ctx: Context) -> None:

    # Input validation
    if not args:
        smf.printf(
            f"[!] WARN => Use the command {CC.GREEN}help{CC.RESET} to see the correct command."
        )
        return

    # Get plugin name from input
    cmd = args[0].lower()
    # Load plugin into memory
    ctx.plugin.load(cmd)
