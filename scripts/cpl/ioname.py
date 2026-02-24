# MIT License

# Copyright (c) 2025 Elzy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Storm-Framework"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
