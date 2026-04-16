import crypt
import smf
from apps.utility.colors import C

MOD_INFO = {
    "Name": "Bruteforce hashing MD5-Crypt",
    "Description": """
Trying thousands of keywords to find a match against the hash
MD5-Crypt.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Bruteforce", {"Description": "Trying thousands of keywords"}],
    ],
    "DefaultAction": "Bruteforce",
    "License": "SMF License",
}
REQUIRED_OPTIONS = {"HASH": "", "PASS": ""}


def execute(options):
    """
    Cracking MD5-Crypt password hashes using wordlists.
    """
    shadow_entry = options.get("HASH")
    wordlist_file = options.get("PASS")

    try:
        parts = shadow_entry.split(":")
        if len(parts) < 2:
            smf.printf(f"{C.ERROR} Input at least (user:hash...)")
            return

        username = parts[0]
        full_hash = parts[1]

        # Salt Extraction for MD5-Crypt ($1$)
        if full_hash.startswith("$1$"):
            # Ensure the MD5-Crypt structure has 3 parts: $1$salt$hash_value
            salt_parts = full_hash.split("$")
            if len(salt_parts) < 3:
                smf.aprintf(f"{C.ERROR} Incomplete MD5-Crypt hash structure.")
                return

            salt_crypt = f"${salt_parts[1]}${salt_parts[2]}"  # Format: $1$t7y583it
        else:
            smf.printf(f"{C.ERROR} Unsupported hash format (Not MD5-Crypt $1$).")
            return
    except Exception as e:
        smf.printf(f"{C.ERROR} Hash parsing error =>", e)
        return

    smf.printf(f"{C.MENU} --- PYTHON SHADOW CRACKER (MD5-Crypt) ---")
    smf.printf(f"{C.MENU} [*] Target User: {username}")
    smf.printf(f"{C.MENU} [*] Hash Type: MD5-Crypt ($1$)")
    smf.printf(f"{C.MENU} [*] Salt: {salt_crypt}")
    smf.printf(f"{C.MENU} [*] Loading Wordlist from: {wordlist_file}")

    try:
        with open(wordlist_file, "r", encoding="latin-1") as f:
            for line in f:
                word = line.strip()
                if not word:
                    continue

                hashed_word = crypt.crypt(word, salt_crypt)
                smf.printf(f"{C.MENU}  Try: {word}{C.RESET}", end="\r")

                if hashed_word == full_hash:
                    smf.printf(
                        f"{C.SUCCESS} [✓] SUCCESSFULLY FOUND U:{username} H:{word}"
                    )
                    smf.printf(
                        f"{C.SUCCESS} --------------------------------------------------"
                    )
                    return

        smf.printf(f"{C.ERROR} \n[-] Failed to find password in wordlist.")

    except KeyboardInterrupt:
        return
    except FileNotFoundError:
        smf.printf(f"{C.ERROR} \n[-] ERROR: Wordlist file not found.")
    except Exception as e:
        smf.printf(f"{C.ERROR} \n[-] Unexpected error while cracking =>", e)
        return
