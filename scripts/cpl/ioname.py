import re
import os


def get_bin_name(path):
    with open(path, "r") as f:
        txt = f.read()
        is_cdylib = "cdylib" in txt
        res = re.findall(
            r'\[(?:\[bin\]|package|lib)\].*?name\s*=\s*"([^"]+)"', txt, re.S
        )
        if res:
            name = res[-1].replace("-", "_")
            if is_cdylib:
                return f"lib{name}.so"
            return name
        return os.path.basename(os.path.dirname(path))


# Looking up I/O names inside Cargo.toml in each Rust function
# [[bin]] always needs to be paid attention to in order to compile stably
# It is important to note that Cargo.toml must always be present alongside Rust code files without src.
