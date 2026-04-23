# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import importlib.util
import importlib.machinery
import sys
import threading
from pathlib import Path
from typing import Dict, Set, Optional, Any

import smf
from apps.utility.colors import CC
from rootmap import ROOT
from .storage import PluginStateStore
from .safe import SafePluginProxy, NullPlugin
from .monitoring import PluginMonitoring
from .introspection import PluginIntrospection


class PluginManager(PluginMonitoring, PluginIntrospection):
    def __init__(self):
        super().__init__()  # Ensure parent classes are initialized
        self.plugin_dir: Path = Path(ROOT) / "plugin"
        self.registry: Dict[str, Any] = {}
        self.store = PluginStateStore()
        self.active_plugins: Set[str] = self.store.load_active_plugins()

        # Thread safety for state mutation (Crucial for Python 3.13 Free-Threading)
        self._lock = threading.RLock()

        # O(1) Path Resolution Cache
        self._plugin_index: Dict[str, Path] = {}

        # Guaranteed existence of root plugin directory
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        # Build index immediately upon initialization
        self._build_index()

    def _build_index(self) -> None:
        """
        O(N) executed ONLY ONCE.
        Membangun Hash Map menggunakan Shallow Scan.
        """
        self._plugin_index.clear()

        for child in self.plugin_dir.iterdir():
            if child.name.startswith(".") or child.name.startswith("__"):
                continue

            # Architecture 1: Package Based
            if child.is_dir():
                init_file = child / "__init__.py"
                if init_file.exists():
                    self._plugin_index[child.name] = init_file

            # Architecture 2: Single File
            elif child.is_file() and child.suffix == ".py":
                plugin_name = child.stem
                if plugin_name not in self._plugin_index:
                    self._plugin_index[plugin_name] = child

    def _resolve_plugin_path(self, plugin_name: str) -> Optional[Path]:
        """O(1) Directory Traversal via Hash Map."""
        return self._plugin_index.get(plugin_name)

    def _purge_module_from_memory(self, plugin_name: str) -> None:
        """
        Hard Cleanup: Removes the main module AND all its submodules.
        Prevents memory leaks and ensures clean reload.
        """
        # Create a list of keys to avoid RuntimeError (dictionary changed size during iteration)
        keys_to_remove = [
            k
            for k in sys.modules
            if k == plugin_name or k.startswith(f"{plugin_name}.")
        ]
        for k in keys_to_remove:
            del sys.modules[k]

        # Clear import caches to ensure Python reads the newest physical file
        importlib.invalidate_caches()

    def boot(self) -> None:
        """Runs when the framework starts, loads all stored plugins."""
        smf.printd("Booting PluginManager", list(self.active_plugins), level="INFO")

        # Iterate over a tuple copy to prevent RuntimeError
        for p_name in tuple(self.active_plugins):
            self._load_module(p_name)

        def _load_module(self, plugin_name: str) -> bool:
        with self._lock:
            # [PERBAIKAN]: Cek eksistensi file SEBELUM masuk ke blok eksekusi yang rawan crash.
            # Jika file tidak ada, langsung tolak tanpa menyentuh registry.
            plugin_path = self._resolve_plugin_path(plugin_name)
            if not plugin_path or not plugin_path.exists():
                smf.printf(f"{CC.YELLOW}[!] Plugin not found on disk =>{CC.RESET}", plugin_name)
                # Kembalikan False tanpa mendaftarkannya ke NullPlugin
                return False

            # Jika file ada secara fisik, baru kita coba kompilasi dan load
            try:
                smf.printd("Resolving module path", plugin_name, level="DEBUG")

                # Low-level Module Specification loading
                spec = importlib.util.spec_from_file_location(plugin_name, str(plugin_path))
                if spec is None or spec.loader is None:
                    raise ImportError(f"Cannot create module spec for {plugin_path}")

                # Instance Module Memory Allocation
                module = importlib.util.module_from_spec(spec)

                # Register to sys.modules BEFORE execution to resolve relative imports
                sys.modules[plugin_name] = module

                # Execute code inside module (Compile AST to Bytecode)
                spec.loader.exec_module(module)

                # Entry Point Validation
                if not hasattr(module, "Plugin"):
                    raise AttributeError(
                        f"Module '{plugin_name}' is missing the main 'Plugin' class."
                    )

                # Initialization & Proxying
                instance = module.Plugin()
                safe_instance = SafePluginProxy(plugin_name, instance)
                self.registry[plugin_name] = safe_instance

                smf.printd("Plugin loaded successfully", plugin_name, level="INFO")
                return True

            except Exception as e:
                # Blok ini sekarang HANYA akan menangkap plugin yang ADA secara fisik, 
                # tetapi rusak secara logika (misal: SyntaxError, ImportError, atau crash saat init).
                # Ini adalah perilaku CRASHED yang valid.
                smf.printf(f"Failed to load plugin =>", plugin_name)
                smf.printd(f"Failed to load plugin [{plugin_name}]", e, level="CRITICAL")
                
                # Daftarkan sebagai NullPlugin HANYA jika file-nya memang ada tapi rusak
                self.registry[plugin_name] = NullPlugin(plugin_name)

                # Purge from memory on partial fail (Clean state)
                self._purge_module_from_memory(plugin_name)
                return False
                
    def load(self, plugin_name: str) -> bool:
        """Command handler to load new plugins."""
        with self._lock:
            # Rebuild index in case it's a newly added file
            self._build_index()

            # Deep purge before load to guarantee fresh read
            self._purge_module_from_memory(plugin_name)

            success = self._load_module(plugin_name)
            if success:
                self.active_plugins.add(plugin_name)
                self.store.save_active_plugins(self.active_plugins)
                smf.printf(
                    f"{CC.GREEN}[✓] Plugin loaded successfully =>{CC.RESET}",
                    plugin_name,
                )
            return success

    def unload(self, plugin_name: str) -> bool:
        """Command handler to explicitly disable plugins."""
        with self._lock:
            if plugin_name in self.registry:
                # 1. Delete instance from registry (RAM)
                del self.registry[plugin_name]
                smf.printd("Plugin instance destroyed", plugin_name, level="DEBUG")

                # 2. Update Persistence
                self.active_plugins.discard(
                    plugin_name
                )  # discard() is safer than remove()
                self.store.save_active_plugins(self.active_plugins)

                # 3. Hard Cleanup (Memory Cache Python)
                self._purge_module_from_memory(plugin_name)

                smf.printf(
                    f"{CC.GREEN}[✓] Plugin unloaded completely =>{CC.RESET}",
                    plugin_name,
                )
                smf.printd("Unloaded", plugin_name, level="INFO")
                return True

            smf.printf(f"{CC.YELLOW}[!] Plugin not found =>{CC.RESET}", plugin_name)
            smf.printd("Unload failed, plugin not found.", plugin_name, level="WARN")
            return False

    def get(self, plugin_name: str) -> Any:
        """Called by caller to get plugin."""
        # Using .get() on dict avoids KeyError and allows returning default
        plugin = self.registry.get(plugin_name)
        if plugin is None:
            smf.printd(
                "Caller requested inactive/missing plugin", plugin_name, level="WARN"
            )
            return NullPlugin(plugin_name)
        return plugin
