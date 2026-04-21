# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
from lib.smfdb_helpers.log_utils import extract_logs
from apps.utility.colors import CC


# This command is used to retrieve specific logs that are stored.
# in the internal log database and differentiated using several log levels
# for example:
# (DEBUG, INFO, WARN, ERROR, CRITICAL)
#
# The commands that can be used are as follows!
#
# smf => export log debug
# smf => export log info
# and so forth.
#
# If the log is successfully retrieved, by default the resulting log file will be saved in HOME.
def execute(args, context):
    # Validate argument length.
    if len(args) >= 2:
        cmd = args[0].lower()
        val = args[1].upper()  # Example val: "CRITICAL", "WARN"

        if cmd == "log":
            # Security Validation (Whitelist)
            valid_levels = {"DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"}
            if val not in valid_levels:
                smf.printf(
                    f"{CC.RED}[!] ERROR => Unknown log level > {val}. Allowed => {', '.join(valid_levels)}{CC.RESET}"
                )
                # Monitor user typos
                smf.printd("Invalid log extraction attempt", val, level="WARN")
                return context

            # Dynamic File Naming (Prevent Overwrite)
            # Example result: "log_CRITICAL.txt"
            output_filename = f"log_{val}.txt"

            # Execute the extractor function with full parameters
            extract_logs(val, output_file=output_filename)
        else:
            # If the user types: take backup, take system, etc.
            smf.printf(
                f"{CC.YELLOW}[!] WARN => Unknown subcommand '{cmd}' for 'export'{CC.RESET}"
            )
    else:
        # If the user just types "take" or "take log" without a level argument
        smf.printf(
            f"{CC.YELLOW}[!] WARN => Syntax error. Usage: export log <level>{CC.RESET}"
        )
        # Log syntax errors to the log database
        smf.printd("CLI Syntax Error", args, level="DEBUG")

    return context
