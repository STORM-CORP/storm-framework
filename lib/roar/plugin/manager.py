# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import importlib.util
import sys
import threading
from pathlib import Path
from typing import Dict, Set, Optional, Any

import smf
from apps.utility.colors import CC
from rootmap import ROOT
from .storage import PluginStateStore
from .safe import SafePluginProxy, NullPlugin

# ==========================================
# STATE MEMORY (Module-Level Singleton)
# Menggantikan peran `self`
# ==========================================
PLUGIN_DIR: Path = Path(ROOT) / "plugin"
REGISTRY: Dict[str, Any] = {}
_store = PluginStateStore()
ACTIVE_PLUGINS: Set[str] = _store.load_active_plugins()

_lock = threading.RLock()
_plugin_index: Dict[str, Path] = {}

# Guaranteed existence of root plugin directory
PLUGIN_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# CORE LOGIC (Pure Functions)
# ==========================================

def build_index() -> None:
    """O(N) executed ONLY ONCE. Membangun Hash Map menggunakan Shallow Scan."""
    _plugin_index.clear()

    for child in PLUGIN_DIR.iterdir():
        if child.name.startswith(".") or child.name.startswith("__"):
            continue

        if child.is_dir():
            init_file = child / "__init__.py"
            if init_file.exists():
                _plugin_index[child.name] = init_file
        elif child.is_file() and child.suffix == ".py":
            _plugin_index[child.stem] = child

def resolve_plugin_path(plugin_name: str) -> Optional[Path]:
    """O(1) Directory Traversal via Hash Map."""
    return _plugin_index.get(plugin_name)

def purge_module_from_memory(plugin_name: str) -> None:
    """Hard Cleanup: Removes the main module AND all its submodules."""
    keys_to_remove = [k for k in sys.modules if k == plugin_name or k.startswith(f"{plugin_name}.")]
    for k in keys_to_remove:
        del sys.modules[k]
    importlib.invalidate_caches()

def get_plugin(plugin_name: str) -> Any:
    """Mengambil proxy plugin dari RAM."""
    plugin = REGISTRY.get(plugin_name)
    if plugin is None:
        smf.printd("Caller requested inactive/missing plugin", plugin_name, level="WARN")
        return NullPlugin(plugin_name)
    return plugin

def load_module(plugin_name: str) -> bool:
    """Fungsi kompilasi AST & Memory Allocation tingkat rendah."""
    with _lock:
        plugin_path = resolve_plugin_path(plugin_name)
        if not plugin_path or not plugin_path.exists():
            smf.printf(f"{CC.YELLOW}[!] Plugin not found on disk =>{CC.RESET}", plugin_name)
            return False

        try:
            smf.printd("Resolving module path", plugin_name, level="DEBUG")

            spec = importlib.util.spec_from_file_location(plugin_name, str(plugin_path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot create module spec for {plugin_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # [REKAYASA ARSITEKTUR] 
            # Tidak ada lagi inisiasi class instance = module.Plugin().
            # Karena plugin sekarang murni fungsional, kita jadikan modul itu sendiri sebagai objeknya!
            safe_instance = SafePluginProxy(plugin_name, module)
            REGISTRY[plugin_name] = safe_instance

            smf.printd("Plugin loaded successfully", plugin_name, level="INFO")
            return True

        except Exception as e:
            smf.printf(f"Failed to load plugin =>", plugin_name)
            smf.printd(f"Failed to load plugin [{plugin_name}]", str(e), level="CRITICAL")
            REGISTRY[plugin_name] = NullPlugin(plugin_name)
            purge_module_from_memory(plugin_name)
            return False

def load(plugin_name: str) -> bool:
    with _lock:
        build_index()
        purge_module_from_memory(plugin_name)
        success = load_module(plugin_name)
        if success:
            ACTIVE_PLUGINS.add(plugin_name)
            _store.save_active_plugins(ACTIVE_PLUGINS)
            smf.printf(f"{CC.GREEN}[✓] Plugin loaded successfully =>{CC.RESET}", plugin_name)
        return success

def unload(plugin_name: str) -> bool:
    with _lock:
        if plugin_name in REGISTRY:
            del REGISTRY[plugin_name]
            ACTIVE_PLUGINS.discard(plugin_name)
            _store.save_active_plugins(ACTIVE_PLUGINS)
            purge_module_from_memory(plugin_name)
            smf.printf(f"{CC.GREEN}[✓] Plugin unloaded completely =>{CC.RESET}", plugin_name)
            return True
        return False

def boot() -> None:
    for p_name in tuple(ACTIVE_PLUGINS):
        load_module(p_name)

def broadcast(event_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for plugin_name, safe_proxy in REGISTRY.items():
        event_hook = getattr(safe_proxy, event_name, None)
        if callable(event_hook):
            try:
                results[plugin_name] = event_hook(*args, **kwargs)
            except Exception as e:
                results[plugin_name] = None
    return results

# ==========================================
# AUTO-EXECUTION (Siklus Hidup Awal)
# ==========================================
# Membangun indeks otomatis saat `import manager` dipanggil pertama kali
build_index()
            
