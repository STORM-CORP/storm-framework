#
# modules/vulnerability/category/name_cve.py
# This is the CVE template and its place is in the top path
# Use the appropriate CVE name to name the .py file and format
# if the existing CVE category does not match the one you want to add
# just create a new folder with the appropriate category name

CVE_INFO = {
    "cve": "CVE-XXXX-XXXX",
    "name": "Vulnerability name",
    "severity": "CRITICAL/HIGH/MEDIUM/LOW",
    "published": "",
    "updated": "",
    "description": """
    Provide a brief description for this vulnerability.
    """,
    "URL": ["Add CVE source link. Example: https://nvd.nist.gov"],
    "scanner": "Enter the scanner name if any",
    "exploit": "Enter the exploit name if there is one",
}
"""
For Scanner and Exploit you can create a script that is suitable for CVE
if and when you have created everything make sure the exploit or scanner name is included
in the CVE you created.
If it's just a CVE without an exploit or scanner, just leave it blank, don't fill it in the CVE.
"""
