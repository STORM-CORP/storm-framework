# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils
from apps.utility.colors import C


# The show command is used to display data in modules.
# such as the following example;
# 1. Command => show modules > will display the modules category.
# 2. Command => show auxiliary > will display all contents in the auxiliary.
# 3. Command => show options > will display global variables.
def execute(args, context):
    target_show = args[0].lower() if args else ""
    current_module = context["current_module"]
    current_module_name = context["current_module_name"]
    options = context["options"]
    if not target_show:
        smf.printf(f"{C.ERROR}[!] No modules selected.{C.RESET}")
        return context

    # 1. show modules
    if target_show == "modules":
        categories = utils.get_categories()
        smf.printf(f"\n{C.HEADER}--- Categories ---{C.RESET}")

        for cat in categories:
            smf.printf(f"  - {cat}")

        smf.printf(f"\n{C.INPUT}[-] WARN => show <category_name> to see modules.{C.RESET}")
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

    # 3. show <category_name>
    else:
        module_files = utils.get_modules_in_category(target_show)
        if module_files:
            smf.printf(f"\n{C.HEADER}Modules in {target_show}:{C.RESET}")
            for mod in module_files:
                smf.printf(f"  - {mod}")
            smf.printf()
        else:
            smf.printf(f"{C.INPUT}[-] Category or option => {target_show} > not found.")

    return context
