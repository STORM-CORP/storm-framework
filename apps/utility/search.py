import os
import smf
import sys
from rootmap import ROOT


def search_modules(query):
    modules_path = os.path.join(ROOT, "modules")
    smf.printf(f"\n[*] Searching for => {query}")
    smf.printf(f"{'Module Path':<35} {'Category'}")
    smf.printf(f"{'-'*35} {'-'*15}")
    count = 0
    if not os.path.exists(modules_path):
        smf.printf(f"[-] Directory not found => {modules_path}")
        return
    for root, dirs, files in os.walk(modules_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_name_only = file.replace(".py", "").lower()

                if query.lower() in file_name_only:
                    count += 1
                    rel_path = os.path.relpath(os.path.join(root, file), modules_path)
                    clean_path = rel_path.replace(".py", "")
                    category = rel_path.split(os.sep)[0]

                    smf.printf(f"{clean_path:<35} {category}")

    if count == 0:
        smf.printf(f"[-] {query} => Not found.")
        smf.printf()
    else:
        smf.printf(f"\n[*] Found {count} module.")
        smf.print()
