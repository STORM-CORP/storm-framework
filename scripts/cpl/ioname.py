# Copyright (c) 2026 Storm Framework

# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import re
import os

def get_bin_name(path):
    with open(path, "r") as f:
        txt = f.read()
        # Search for name in block [[bin]]
        res = re.findall(r'\[(?:\[bin\]|package)\].*?name\s*=\s*"([^"]+)"', txt, re.S)
        return res[-1].replace("-", "_") if res else os.path.basename(os.path.dirname(path))

# Looking up I/O names inside Cargo.toml in each Rust function
# [[bin]] always needs to be paid attention to in order to compile stably
# It is important to note that Cargo.toml must always be present alongside Rust code files without src.
