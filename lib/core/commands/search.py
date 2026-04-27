# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
from apps.utility.search import search_modules
from lib.smf.core.console.engine import Context


# Search command to search for the modules we want to search for
# This is very dynamic as in general it does not require specific words.
# if there is a module name scan_a, scan_b, and you run it like;
#
# Command => search <value>
#
# then all module names containing the word scan will appear completely.
def execute(args: list[str], ctx: Context) -> None:
    query = args[0] if args else ""
    if not query:
        smf.printf("[!] Enter file name to search!")
    else:
        search_modules(query)
