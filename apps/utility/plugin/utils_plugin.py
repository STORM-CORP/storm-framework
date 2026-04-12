import importlib.util
from pathlib import Path
from typing import Dict
from types import ModuleType

# internal import
from apps.utility.colors import C
from rootmap import ROOT

# ---------------------------------------------------------
# MODULE-LEVEL STATE
# Menggantikan self.registry dan self.plugin_dir
# ---------------------------------------------------------
_REGISTRY: Dict[str, ModuleType] = {}
PLUGIN_DIR = Path(ROOT) / "plugin"


def _dynamic_import(name: str, path: Path) -> ModuleType:
    """Dynamically import modules into memory from absolute paths"""

    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create module spec for {name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def start_load_plugins() -> None:
    """Runs once when the framework is first run"""

    if not PLUGIN_DIR.exists() or not PLUGIN_DIR.is_dir():
        print(f"{C.ERROR}[!] ERROR => Invalid plugin directory > {PLUGIN_DIR}")
        return

    try:
        # Gunakan rglob untuk mencari file .py secara rekursif
        for file_path in PLUGIN_DIR.rglob("*.py"):
            # Abaikan file dunder (seperti __init__.py)
            if file_path.name.startswith("__"):
                continue

            plugin_name = file_path.stem

            # Isolasi try-except per plugin.
            # Jika 1 plugin error (syntax/import), framework tetap berjalan.
            try:
                # 1. Load modul ke memori
                module = _dynamic_import(plugin_name, file_path)

                # 2. Validasi struktur plugin
                plugin_func = getattr(module, "plugin", None)
                if callable(plugin_func):

                    # Eksekusi event startup
                    response = plugin_func({"event": "startup"})

                    # Simpan referensi ke memory registry
                    _REGISTRY[plugin_name] = module

                    # 3. Evaluasi auto-start secara aman
                    # Memastikan response adalah mapping/dict sebelum memanggil .get()
                    if isinstance(response, dict) and response.get("auto_start"):
                        plugin_func({"event": "command"})

            except Exception as e:
                print(f"{C.ERROR}[!] ERROR LOADING PLUGIN => {plugin_name} > {e}")

    except KeyboardInterrupt:
        print("\nStop startup Storm Framework")
    except Exception as e:
        print(f"{C.ERROR}[!] FATAL ERROR PLUGIN ENGINE => {e}")


def run_plugin(name_plugin: str) -> None:
    """To run the plugin manually"""

    # Gunakan walrus operator (:=) untuk lookup dan assignment efisien
    if module := _REGISTRY.get(name_plugin):
        try:
            module.plugin({"event": "command"})
        except Exception as e:
            print(f"{C.ERROR}[!] PLUGIN ERROR => {name_plugin} > {e}")
    else:
        print(f"{C.INPUT}[-] plugin => {name_plugin} > Not found")
