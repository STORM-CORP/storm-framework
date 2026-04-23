# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils
from apps.utility.colors import C
from lib.smf.core.console.engine import Context


# The set command is used to save data to global variables and module variables.
# it seems like the following example
# Command => set <var> <val>
# or
# Command => set ip 192.168.1.0
# a command like this will insert value data into the variable we implement.
def execute(args: list[str], ctx: Context) -> None:
    options = ctx.options

    if len(args) >= 2:
        var_name = args[0].upper()
        var_value = args[1]

        if var_name not in options:
            smf.printf(
                f"{C.ERROR}[-] ERROR => {var_name} > is not a valid options!{C.RESET}"
            )
            return

        if "PASS" in var_name:
            found_path = utils.resolve_path(var_value)

            if found_path:
                options[var_name] = found_path
                smf.printf(f"{var_name} => {found_path}")
            else:
                smf.printf(f"{C.INPUT}[-] WARN => {var_value} > not found!{C.RESET}")
        else:
            options[var_name] = var_value
            smf.printf(f"{var_name} => {var_value}")
    else:
        smf.printf(f"{C.INPUT}[!] Try => set <VAR> <VALUE>{C.RESET}")
