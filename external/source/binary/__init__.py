import os
import importlib.util

_current_path = os.path.dirname(__file__)


def _load_binaries():
    """Otomatis mengekspos semua file .so ke dalam namespace package ini"""
    for file in os.listdir(_current_path):
        if file.endswith(".so"):
            module_name = file[:-3]
            file_path = os.path.join(_current_path, file)

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                globals()[module_name] = module


_load_binaries()
