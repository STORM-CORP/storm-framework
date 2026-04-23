# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.update import run_update as update
from apps.utility.verify import run_verif as verify
from apps.utility.restart import run_restart as restart
from apps.utility.colors import C

from lib.smf.core.console.engine import Context


# This command storm is used for several specific command values.
# for example give this;
# 1. Command => storm update > to update the Storm Framework.
# 2. Command => storm verify > to re-verify by activating the integrity check.
# 3. Command => storm restart > to restart storm if there are any strange bugs or errors after the update.
def execute(args: list[str], ctx: Context) -> None:
    cmd = args[0].lower() if args else ""
    options = ctx.options
    
    if not cmd:
        smf.printf(f"{C.ERROR}[!] ERROR => Not module selected")
        return

    # I don't understand this update command, which sometimes happens when there is a big and sensitive update.
    # then sometimes integrity detects a missing file, which indicates that there is an identity but the file is missing on the disk
    # but I still recommend reinstalling for security and stability
    if cmd == "update":
        status = update()
        if status == True:
            restart(options)

    # This verify calls an integrity check to ensure there have been no code modifications.
    # when executing the code, and if it detects an injection file without a clear identity
    # This process will force the storm to stop, for the safety of the user.
    elif cmd == "verify":
        verify()

    # This is to restart and save the variables that were set before restarting and then restore them.
    # This is good if we experience a bug or error failure when we are ready to execute.
    # by storing old variable data, it is very profitable and speeds up the time
    elif cmd == "restart":
        restart(options)
    else:
        smf.printf(f"{C.INPUT}[-] WARN => {cmd} > Not found.")

    return
