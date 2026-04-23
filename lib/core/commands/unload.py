# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import CC
from lib.roar.plugin.manager import PluginManager
from lib.smf.core.console.engine import Context


def execute(args: list[str], ctx: Context) -> None:

    if not args:
        smf.printf(
            f"{CC.RED}[!] ERROR => Invalid syntax. Run help to see the correct command.{CC.RESET}"
        )
        return

    cmd = args[0].lower
    ctx.plugin.unload(cmd)
