# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from apps.utility.colors import C
import apps.utility.utils as utils


# Run command to run a module that we want to execute
# The workflow is as below;
# Command => use <module_name>
# Command => set <var> <val>
# Command => run
##
# After running the module will run and you just have to wait for it to finish.
def execute(args, context):
    current_module = context["current_module"]
    options = context["options"]
    if not current_module:
        print(f"{C.ERROR}[!] No modules selected. 'use <module>' first.")
        print()
        return context
    # Get the list of required variables from the selected module.
    required_vars = getattr(current_module, "REQUIRED_OPTIONS", {})
    missing = [
        key for key in required_vars.keys() if not str(options.get(key, "")).strip()
    ]
    if missing:
        print(f"{C.ERROR}[!] Failed to run. Variabel null.")
        print("")
        return context

    try:
        # Automatically check if there is a PASS (Wordlist) so that the path is correct
        if options.get("PASS"):
            full_path = utils.resolve_path(options["PASS"])
            if full_path:
                options["PASS"] = full_path

        # Run the main function of the module
        current_module.execute(options)

    except AttributeError as d:
        print(f"{C.ERROR}[-] ERROR => {d}")
    except Exception as e:
        print(f"{C.ERROR}[-] Error during execution => {e}")

    return context
