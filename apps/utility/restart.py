import os
import sys
import smf
import lib.smf.core.sf.svch as svch


def run_restart(options):
    # save old variables
    svch.session(options)
    # Restart the storm
    executable = sys.argv[0]
    args = sys.argv
    try:
        os.execv(executable, args)
    except Exception as e:
        smf.printd("ERROR RESTART", e, level="ERROR")
        smf.printf(f"[!] Restart failed")
        sys.exit(1)
