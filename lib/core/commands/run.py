# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import sys
import apps.utility.utils as utils
from apps.utility.colors import C
from lib.smf.core.console.engine import Context


# Run command to run a module that we want to execute
# The workflow is as below;
#
# Command => use <module_name>
# Command => set <var> <val>
# Command => run
#
# After running the module will run and you just have to wait for it to finish.
def execute(args: list[str], ctx: Context) -> None:
    current_module = ctx.current_module
    options = ctx.options

    if not current_module:
        smf.printf(f"{C.ERROR}[!] No modules selected. 'use <module>' first.{C.RESET}")
        smf.printf()
        return

    # Get the list of required variables from the selected module.
    required_vars = getattr(current_module, "REQUIRED_OPTIONS", {})
    missing = [
        key for key in required_vars.keys() if not str(options.get(key, "")).strip()
    ]

    if missing:
        smf.printf(f"{C.ERROR}[!] Failed to run. Variabel null.{C.RESET}")
        smf.printf()
        return

    try:
        # Automatically check if there is a PASS (Wordlist) so that the path is correct
        if options.get("PASS"):
            full_path = utils.resolve_path(options["PASS"])
            if full_path:
                options["PASS"] = full_path

        # Run the main function of the module
        current_module.execute(options)

    except AttributeError as d:
        smf.printd("ERROR COMMAND RUN", d, level="ERROR")
        smf.printf(f"{C.ERROR}[!] RUN ATTRIBUTE ERROR.{C.RESET}")
    except Exception as e:
        smf.printd("ERROR COMMAND RUN EXCEPTION", e, level="ERROR")
        smf.printf(
            f"{C.ERROR}[!] Error during execution.{C.RESET}"
        )
