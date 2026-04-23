# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils
from apps.utility.colors import C
from lib.smf.core.console.engine import Context


# Command use to lock or use a module that you want to use.
# here's an example as follows;
# Command => use <val>
# or
# Command => use scan
# in the input zone it will change to lock the scan so we know again
# using what module.
def execute(args: list[str], ctx: Context) -> None:
    module_name = args[0].lower() if args else ""
    mod = utils.load_module_dynamically(module_name)

    current_module = ctx.current_module
    current_module_name = ctx.current_module_name
    
    if mod:
        current_module["current_module"] = mod
        current_module_name["current_module_name"] = module_name
    else:
        smf.printf(f"{C.INPUT}[-] WARN => {module_name} > Not found.")
