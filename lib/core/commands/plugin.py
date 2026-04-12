# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from apps.utility.plugin.utils_plugin import run_plugin
from apps.utility.colors import C


def execute(args, context):
    cmd = args[0].lower() if args else ""

    if not cmd:
        print(f"{C.ERROR}[!] ERROR => Not module selected")
        print()
        return context

    else:
        run_plugin(cmd)

    return context
