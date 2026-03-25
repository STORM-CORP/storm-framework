from app.utility.update import run_update as update
from app.utility.verify import run_verif as verify
from app.utility.restart import run_restart as restart
from app.utility.colors import C


def execute(args, context):
    cmd = args[0].lower() if args else ""
    if not cmd:
        print(f"{C.ERROR}[!] ERROR => Not module selected")
        return context

    # I don't understand this update command, which sometimes happens when there is a big and sensitive update.
    # then sometimes integrity detects a missing file, which indicates that there is an identity but the file is missing on the disk
    # but I still recommend reinstalling for security and stability
    if cmd == "update":
        status = update()
        if status == True:
            restart(context)

    # This verify calls an integrity check to ensure there have been no code modifications.
    # when executing the code, and if it detects an injection file without a clear identity
    # This process will force the storm to stop, for the safety of the user.
    elif cmd == "verify":
        verify()

    # This is to restart and save the variables that were set before restarting and then restore them.
    # This is good if we experience a bug or error failure when we are ready to execute.
    # by storing old variable data, it is very profitable and speeds up the time
    elif cmd == "restart":
        restart(context)
    else:
        print(f"{C.INPUT}[-] WARN => {cmd} > Not found.")

    return context
