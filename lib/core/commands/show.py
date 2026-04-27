# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils
from apps.utility.colors import CC
from lib.smf.core.console.engine import Context


# The show command is used to display data in modules.
# such as the following example;
# 1. Command => show modules > will display the modules category.
# 2. Command => show auxiliary > will display all contents in the auxiliary.
# 3. Command => show options > will display global variables.
# 4. Command => show plugin > will display all existing plugins.
def execute(args: list[str], ctx: Context) -> None:
    target_show = args[0].lower() if args else ""

    current_module = ctx.current_module
    current_module_name = ctx.current_module_name
    options = ctx.options
    plugin = ctx.plugin

    if not target_show:
        smf.printf("[!] No modules selected.")
        return

    # 1. show modules
    if target_show == "modules":
        categories = utils.get_categories()
        smf.printf("\n[--- Categories ---]")

        for cat in categories:
            smf.printf(f"  - {cat}")

        smf.printf("\n[!] WARN => show <category_name> to see modules.")
        smf.printf()

    # 2. show options
    elif target_show == "options":
        header_name = current_module_name if current_module else "GLOBAL"
        smf.printf(f"\nMODULE OPTIONS ({header_name}):")
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

    # 3. show plugin
    elif target_show == "plugin":
        status_list = plugin.monitor()

        if not status_list:
            smf.printf(f"[!] No plugins found in {manager.plugin_dir}")
            return

        # Header Tabel
        smf.printf(f"\n{'PLUGIN NAME':<25} {'STATUS':<10}")
        smf.printf(f"{'-' * 36}")

        for item in status_list:
            name = item["name"]
            status = item["status"]

            # Pewarnaan Status
            color = CC.WHITE
            if status == "ACTIVE":
                color = CC.GREEN
            elif status == "CRASHED":
                color = CC.RED
            elif status == "NON-ACTIVE":
                color = CC.YELLOW
            elif status == "ORPHANED":
                color = CC.BLUE

            smf.printf(f"{name:<25} {color}{status:<10}{CC.RESET}")

        smf.printf(f"{'-' * 36}\n")

    # 4. show <category_name>
    else:
        module_files = utils.get_modules_in_category(target_show)
        if module_files:
            smf.printf(f"\nModules in {target_show}:")
            for mod in module_files:
                smf.printf(f"  - {mod}")
            smf.printf()
        else:
            smf.printf(f"[!] WARN => {target_show} > not found.")
