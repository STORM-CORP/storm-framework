# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from lib.smf.core.console.engine import Context


# This command is used to turn off the plugin life cycle.
# active, in the following way;
#
# Command => unload <plugin_name>
#
# It will directly disable the active plugin.
def execute(args: list[str], ctx: Context) -> None:

    # Input validation
    if not args:
        smf.printf("[!] WARN => Use the command => unload <plugin_name>")
        return

    # Get plugin name command
    cmd = args[0].lower()
    # Unload plugin name
    ctx.plugin.unload(cmd)
