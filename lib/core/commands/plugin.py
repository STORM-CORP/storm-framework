# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from apps.utility.plugin import utils_plugin as upl
from apps.utility.colors import C


# The plugin command is used to run the plugin manually
# and here's how to use it
# command => plugin <name_plugin>
#
# Simple example:
# command => plugin example
#
# This manual logic only runs in the session when the storm is running
# it will not be permanent if you (exit) the plugin automatically False
# and you need to rerun it every time you run Storm.
def execute(args, context):
    cmd = args[0].lower() if args else ""

    if not cmd:
        print(f"{C.ERROR}[!] ERROR => Not module selected")
        print()
        return context
    else:
        upl.run_plugin(cmd)

    return context
