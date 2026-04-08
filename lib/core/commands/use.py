# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import apps.utility.utils as utils
from apps.utility.colors import C


# Command use to lock or use a module that you want to use.
# here's an example as follows;
# Command => use <val>
# or
# Command => use scan
# in the input zone it will change to lock the scan so we know again
# using what module.
def execute(args, context):
    module_name = args[0].lower() if args else ""
    mod = utils.load_module_dynamically(module_name)

    if mod:
        context["current_module"] = mod
        context["current_module_name"] = module_name
    else:
        print(f"{C.INPUT}[-] WARN => {module_name} > Not found.")

    return context
