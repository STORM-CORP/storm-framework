import os
import random
import importlib
from app.utility.colors import C
from rootmap import ROOT


def get_random_banner():
    banner_dir = os.path.join(ROOT, "lib", "ui", "banners")
    try:
        if not os.path.exists(banner_dir):
            return f"{C.SUCCESS}[!] Folder Not Found => {banner_dir}"
        all_files = [
            f
            for f in os.listdir(banner_dir)
            if f.endswith(".py") and f != "__init__.py"
        ]

        if not all_files:
            return f"{C.SUCCESS}Storm Framework"

        random_file = random.choice(all_files)
        module_path = f"lib.ui.banners.{random_file.replace('.py', '')}"

        # Reload module if necessary or import normally
        banner_module = importlib.import_module(module_path)
        raw_banner = getattr(banner_module, "DATA", "Banner not found.")

        lines = raw_banner.splitlines()

        if not lines:
            return raw_banner

        padding_str = " " * 5

        result = "\n".join([f"{padding_str}{line}" for line in lines])

        return result
    except Exception as e:
        return f"Error loading banner => {e}"
