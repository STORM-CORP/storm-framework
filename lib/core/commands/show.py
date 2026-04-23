# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils
from apps.utility.colors import *
from lib.smf.core.console.engine import Context


# The show command is used to display data in modules.
# such as the following example;
# 1. Command => show modules > will display the modules category.
# 2. Command => show auxiliary > will display all contents in the auxiliary.
# 3. Command => show options > will display global variables.
def execute(args: list[str], ctx: Context) -> None:
    target_show = args[0].lower() if args else ""

    current_module = ctx.current_module
    current_module_name = ctx.current_module_name
    options = ctx.options
    plugin = ctx.plugin

    if not target_show:
        smf.printf(f"{C.ERROR}[!] No modules selected.{C.RESET}")
        return

    # 1. show modules
    if target_show == "modules":
        categories = utils.get_categories()
        smf.printf(f"\n{C.HEADER}--- Categories ---{C.RESET}")

        for cat in categories:
            smf.printf(f"  - {cat}")

        smf.printf(
            f"\n{C.INPUT}[-] WARN => show <category_name> to see modules.{C.RESET}"
        )
        smf.printf()

    # 2. show options
    elif target_show == "options":
        header_name = current_module_name if current_module else "GLOBAL"
        smf.printf(f"\n{C.HEADER}MODULE OPTIONS ({header_name}):{C.RESET}")
        smf.printf(f"{'Name':<12} {'Current Setting':<25} {'Description'}")
        smf.printf(f"{'-'*12} {'-'*25} {'-'*15}")

        if current_module:
            req = getattr(current_module, "REQUIRED_OPTIONS", {})
            for var_name, desc in req.items():
                val = options.get(var_name, "unset")
                smf.printf(f"{var_name:<12} {val:<25} {desc}")
        else:
            for k, v in options.items():
                val = v if v else "unset"
                smf.printf(f"{k:<12} {val:<25} Global Variable")
        smf.printf()

    elif target_show == "plugin":
        status_list = plugin.get_status_map()

        if not status_list:
            smf.printf(f"{CC.WARN}[!] No plugins found in {manager.plugin_dir}{CC.RESET}")
            return

        # Header Tabel
        smf.printf(f"\n{CC.CYAN}{'PLUGIN NAME':<25} {'STATUS':<10}{CC.RESET}")
        smf.printf(f"{CC.CYAN}{'-' * 36}{CC.RESET}")

        for item in status_list:
            name = item['name']
            status = item['status']

            # Pewarnaan Status
            color = CC.WHITE
            if status == "ACTIVE":
                color = CC.GREEN
            elif status == "CRASHED":
                color = CC.RED
            elif status == "INACTIVE":
                color = CC.YELLOW

            smf.printf(f"{name:<25} {color}{status:<10}{CC.RESET}")
        
        smf.printf(f"{CC.CYAN}{'-' * 36}{CC.RESET}\n")
    

    # 4. show <category_name>
    else:
        module_files = utils.get_modules_in_category(target_show)
        if module_files:
            smf.printf(f"\n{C.HEADER}Modules in {target_show}:{C.RESET}")
            for mod in module_files:
                smf.printf(f"  - {mod}")
            smf.printf()
        else:
            smf.printf(f"{C.INPUT}[-] WARN => {target_show} > not found.{C.RESET}")
