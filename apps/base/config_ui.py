import json
import os
import smf

import apps.utility.utils as utils
from apps.utility.colors import C
from rootmap import ROOT


def show_about():
    data = os.path.join(ROOT, "data", "data_version.json")
    with open(data) as f:
        VERSION = json.load(f)["version"]

    smf.printf(
        f"\n{C.HEADER}=========================================================================="
    )
    smf.printf(
        f"{C.HEADER}=========================================================================="
    )
    smf.printf(f"{C.INPUT}      owner                     : エルジー")
    smf.printf(f"{C.INPUT}      Purpose                   : All-in-One Pentest Tools")
    smf.printf(f"{C.INPUT}      Version                   : {VERSION}")
    smf.printf(
        f"{C.INPUT}      GitHub                    : github.com/StormWorld0/storm-framework"
    )
    smf.printf(
        f"{C.HEADER}==========================================================================\n"
    )


def show_help():
    smf.printf(f"""
{C.HEADER}==========================================================================
{C.SUCCESS}                             COMMAND GUIDE
{C.HEADER}==========================================================================
{C.INPUT}
  help                          : Displaying the manual
  show options                  : View the variables that have been set
  show modules                  : Displaying module categories
  show <name_categories>        : Displays the complete contents


  take log <val>                : Take logs from internal database and save as txt
  search <filename>             : To search for files
  about                         : Information Development
  info <cve_name>               : Complete CVE information
  info <module_name>            : Complete Modules information
  back                          : Back from current position
  clear                         : Clear command line
  exit                          : Exit the application

  
  use <nama_modul>              : Selecting a module
  set <key> <val>               : Filling in the parameters
  run                           : Run the selected module


  storm update                  : Make updates if necessary
  storm verify                  : Used to check the signature of all files
  storm restart                 : To restart if you experience a bug or error
{C.HEADER}==========================================================================
    """)


def stormUI():
    total = utils.count_modules()
    stats = utils.count_by_category()

    # 1. Create a list containing strings for each category.
    # Example: ["MODULE: 15", "EXPLOIT: 2", "AUXILIARY: 11", "VULNERABILITY: 2"]
    items = [f"MODULE: {total}"] + [f"{k.upper()}: {v}" for k, v in stats.items()]

    # 2. Group items max 3
    max_items_per_row = 3
    for i in range(0, len(items), max_items_per_row):
        row_items = items[i : i + max_items_per_row]

        # 3. Combine only the items in that row with " | "
        line_text = " | ".join(row_items)

        # 4. Decorative print
        smf.printf(f"{C.HEADER}+-- --=[ {C.INPUT}{line_text} {C.HEADER}]=--{C.RESET}")

    smf.printf()
    smf.printf("The Storm Framework is a StormWorld0 Open Source Project")
    smf.printf(f"Run {C.SUCCESS}about{C.RESET} to view dev information.")
    smf.printf()
