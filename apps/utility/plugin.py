import importlib.util
from pathlib import Path
from typing import Dict, Any
from types import ModuleType

# Asumsi impor dari struktur framework Anda
from apps.utility.colors import C
from rootmap import ROOT

# ---------------------------------------------------------
# MODULE-LEVEL STATE
# Menggantikan self.registry dan self.plugin_dir
# ---------------------------------------------------------
_REGISTRY: Dict[str, ModuleType] = {}
PLUGIN_DIR = Path(ROOT) / "plugin"


def _dynamic_import(name: str, path: Path) -> ModuleType:
    """Mengimpor modul secara dinamis ke dalam memori dari absolute path."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Gagal membuat module spec untuk {name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def start_load_plugins() -> None:
    """Dijalankan sekali saat framework pertama kali dibuka."""
    if not PLUGIN_DIR.exists() or not PLUGIN_DIR.is_dir():
        print(f"{C.ERROR}[!] ERROR => Direktori plugin tidak valid: {PLUGIN_DIR}")
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

                # Simpan referensi ke memory registry
                _REGISTRY[plugin_name] = module

            except Exception as e:
                print(f"{C.ERROR}[!] ERROR MEMUAT PLUGIN '{plugin_name}' => {e}")

    except KeyboardInterrupt:
        print("\nStop startup Storm Framework")
    except Exception as e:
        print(f"{C.ERROR}[!] FATAL ERROR PLUGIN ENGINE => {e}")


def run_plugin(name_plugin: str, data: dict = None) -> None:
    """Dijalankan saat user ngetik: plugin <name_plugin>"""

    # Gunakan walrus operator (:=) untuk lookup dan assignment efisien
    if module := _REGISTRY.get(name_plugin):
        try:
            module.plugin(data or {"event": "run"})
        except Exception as e:
             print(f"{C.ERROR}[!] ERROR SAAT MENJALANKAN PLUGIN '{name_plugin}' => {e}")
    else:
        print(f"{C.INPUT}[-] Plugin => {name_plugin} > Not found")


def get_plugin(name: str):
    return _REGISTRY.get(name)
