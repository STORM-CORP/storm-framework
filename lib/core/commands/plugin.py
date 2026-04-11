# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from apps.utility.plugin import utils_plugin as up
from apps.utility.colors import C

def execute(args, context):
    cmd = args[0].lower() if args else ""

    if not cmd:
        print(f"{C.ERROR}[!] ERROR => Not module selected")
        print()
        return context

    else:
        up.run_plugin(cmd)

    return context
