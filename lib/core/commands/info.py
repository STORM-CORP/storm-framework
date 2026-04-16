# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import importlib.util
import textwrap
import smf
import sys

from apps.utility.colors import C


# For those who like CVE collections, this logic is definitely needed
# Because this will produce output that is neat in structure and style.
# For ease of reading, and to differentiate between Description, name, ID, etc.
# The most important thing is to make sure that the CVE uses the example data format that has been provided.
# Otherwise the output will be messy and not according to storm rules.
def execute(args, context):
    query = args[0] if args else ""
    if not query:
        smf.printf("{C.ERROR}[-] Enter file name to info!")
        return context

    # This is a special logic to know where the CVE is located.
    # Make sure CVE is always in the vulnerability folder
    vuln_path = "modules/"
    found_path = ""
    for root, dirs, files in os.walk(vuln_path):
        if f"{query}.py" in files:
            found_path = os.path.join(root, f"{query}.py")
            break

    filename = os.path.basename(found_path).lower()
    if found_path:
        if filename.startswith("cve"):
            # Used to display cve // vulnerability information
            # Command => info <cve_name>
            try:
                spec = importlib.util.spec_from_file_location("temp_mod", found_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                # --- GET DICTIONARY CVE_INFO ---
                info = mod.CVE_INFO
                width = 55

                smf.printf()
                smf.printf(f"\n{C.HEADER}{'='*width}")
                smf.printf(f"{C.SUCCESS}{'STORM VULNERABILITY KNOWLEDGE BASE':^55}")
                smf.printf(f"{C.HEADER}{'='*width}")

                smf.printf(f"{C.SUCCESS}{'ID CVE':<13} : {info['cve']}")
                smf.printf(f"{C.SUCCESS}{'NAME':<13} : {info['name']}")
                smf.printf(f"{C.SUCCESS}{'LEVEL':<13} : {info['severity']}")
                smf.printf(f"{C.SUCCESS}{'PUBLISHED':<13} : {info['published']}")
                smf.printf(f"{C.SUCCESS}{'UPDATED':<13} : {info['updated']}")
                smf.printf(f"{C.HEADER}{'-'*width}")

                smf.printf(f"{C.SUCCESS}DESCRIPTION   :")
                desc = textwrap.fill(
                    info["description"].strip(),
                    width=width - 2,
                    initial_indent=" ",
                    subsequent_indent=" ",
                )
                smf.printf(desc)

                smf.printf(f"{C.HEADER}{'-'*width}")
                smf.printf(f"{C.SUCCESS}REFERENCES    :")
                for link in info["URL"]:
                    smf.printf(f" - {link}")
                smf.printf(f"{C.HEADER}{'-'*width}")

                smf.printf(f"{C.SUCCESS}{'SCANNER':<13} : {info['scanner']}")
                smf.printf(f"{C.SUCCESS}{'EXPLOIT':<13} : {info['exploit']}")
                smf.printf(f"{C.HEADER}{'='*width}\n")
                smf.printf()

            except Exception as e:
                smf.printf(f"{C.ERROR}[-] Failed to read =>", e, file=sys.stderr, flush=True)

        else:
            # To display information about a specific module
            # Command => info <modules_name>
            try:
                spec = importlib.util.spec_from_file_location("temp_mod", found_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                # --- GET DICTIONARY MOD_INFO ---
                info = mod.MOD_INFO
                width = 55
                label_w = 13

                smf.printf()
                smf.printf(f"{C.HEADER}{'='*width}")
                smf.printf(f"{C.SUCCESS}{'STORM INFORMATION MODULES':^55}")
                smf.printf(f"{C.HEADER}{'='*width}")

                smf.printf(f"{C.SUCCESS}{'NAME':<13} : {info['Name']}")
                smf.printf(f"{C.SUCCESS}DESCRIPTION   :")
                desc = textwrap.fill(
                    info["Description"].strip(),
                    width=width - 2,
                    initial_indent=" ",
                    subsequent_indent=" ",
                )
                smf.printf(desc)

                smf.printf(f"{C.HEADER}{'-'*width}")
                authors = info.get("Author", [])
                first_auth = authors[0] if authors else "Unknown"
                smf.printf(f"{C.SUCCESS}{'AUTHOR':<{label_w}} : - {first_auth}")
                for extra in authors[1:]:
                    smf.printf(f"{C.SUCCESS}{' '*(label_w)} : - {extra}")

                smf.printf(f"{C.HEADER}{'-'*width}")
                smf.printf(f"{C.SUCCESS}{'ACTION':<13}")
                for action in info.get("Action", []):
                    name = action[0]
                    desc = action[1].get("Description", "")
                    smf.printf(f"{C.SUCCESS}  > {name:<9} : {desc}")

                smf.printf(f"{C.HEADER}{'-'*width}")
                smf.printf(f"{C.SUCCESS}{'DefAction':<13} : {info['DefaultAction']}")
                smf.printf(f"{C.SUCCESS}{'LICENSE':<13} : {info['License']}")
                smf.printf(f"{C.HEADER}{'='*width}")
                smf.printf()

            except Exception as e:
                smf.printf(f"{C.ERROR}[-] Failed to read =>", e, file=sys.stderr, flush=True)
    else:
        smf.printf(f"{C.INPUT}[-] WARN => {query} > not found.")

    return context
