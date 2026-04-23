import os
import sys
import smf
import lib.smf.core.sf.svch as svch
from lib.smf.core.console.engine import Context

def run_restart(ctx: Context):
    # save old variables
    svch.session(ctx.options)
    # Restart the storm
    executable = sys.argv[0]
    args = sys.argv
    try:
        os.execv(executable, args)
    except Exception as e:
        smf.printf(f"[-] Restart failed =>", e, file=sys.stderr, flush=True)
        sys.exit(1)
