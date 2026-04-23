# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import importlib.util
import sys
import smf
import os

from rootmap import ROOT
from .storage import PluginStateStore
from .safe import SafePluginProxy, NullPlugin


class PluginManager:
    def __init__(self):
        self.plugin_dir = os.path.join(ROOT, "plugin")
        self.registry = {}
        self.store = PluginStateStore()
        self.active_plugins = self.store.load_active_plugins()

        # Garansi keberadaan direktori plugin root
        os.makedirs(self.plugin_dir, exist_ok=True)

    def _resolve_plugin_path(self, plugin_name):
        """
        O(N) Directory Traversal.
        Mencari plugin secara rekursif di dalam self.plugin_dir.
        Mendukung 2 arsitektur plugin:
        1. Single File   : /subfolder/namaplugin.py
        2. Package Based : /subfolder/namaplugin/__init__.py
        """
        for root, dirs, files in os.walk(self.plugin_dir):
            # Skenario 1: File tunggal (namaplugin.py)
            target_file = f"{plugin_name}.py"
            if target_file in files:
                return os.path.join(root, target_file)

            # Skenario 2: Berbasis direktori (namaplugin/__init__.py)
            if os.path.basename(root) == plugin_name and "__init__.py" in files:
                return os.path.join(root, "__init__.py")

        return None

    def boot(self):
        """Dijalankan saat framework start, me-load semua plugin yang tersimpan di cache."""
        smf.printd("Booting PluginManager", list(self.active_plugins), level="INFO")

        # Iterasi dari copy (list) agar modifikasi pada set tidak memicu RuntimeError
        for p_name in list(self.active_plugins):
            self._load_module(p_name)

    def _load_module(self, plugin_name):
        try:
            smf.printd("Resolving module path", plugin_name, level="DEBUG")

            # 1. Path Resolution
            plugin_path = self._resolve_plugin_path(plugin_name)
            if not plugin_path:
                raise FileNotFoundError(
                    f"Plugin '{plugin_name}' not found in {self.plugin_dir} or its subdirectories."
                )

            # 2. Low-level Module Specification loading (Mencegah sys.path pollution)
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot create module spec for {plugin_path}")

            # 3. Instance Module Memory Allocation
            module = importlib.util.module_from_spec(spec)

            # 4. Daftarkan ke sys.modules (Dibutuhkan jika plugin melakukan relative import)
            sys.modules[plugin_name] = module

            # 5. Eksekusi kode di dalam module (Compile AST to Bytecode)
            spec.loader.exec_module(module)

            # 6. Validasi Entry Point
            if not hasattr(module, "Plugin"):
                raise AttributeError(
                    f"Module '{plugin_name}' is missing the main 'Plugin' class."
                )

            # 7. Inisialisasi & Proxying
            instance = module.Plugin()
            safe_instance = SafePluginProxy(plugin_name, instance)
            self.registry[plugin_name] = safe_instance

            smf.printf("Plugin loaded successfully =>", plugin_name)
            smf.printd("Plugin loaded successfully", plugin_name, level="INFO")
            return True

        except Exception as e:
            smf.printf("Failed to load plugin =>", plugin_name)
            smf.printd(f"Failed to load plugin [{plugin_name}]", e, level="CRITICAL")
            self.registry[plugin_name] = NullPlugin(plugin_name)

            # Hapus dari sys.modules jika load gagal sebagian (Clean state)
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]

            return False

    def load(self, plugin_name):
        """Command handler untuk me-load plugin baru."""
        # Jika memuat ulang (reload), kita hapus dulu dari memori agar interpreter
        # dipaksa membaca file fisis terbaru (menggantikan importlib.reload)
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]

        success = self._load_module(plugin_name)
        if success:
            self.active_plugins.add(plugin_name)
            self.store.save_active_plugins(self.active_plugins)
        return success

    def unload(self, plugin_name):
        """Command handler untuk mematikan plugin."""
        if plugin_name in self.registry:
            del self.registry[plugin_name]
            smf.printd("Plugin instance destroyed", plugin_name, level="DEBUG")

        if plugin_name in self.active_plugins:
            self.active_plugins.remove(plugin_name)
            self.store.save_active_plugins(self.active_plugins)

        # Hard Cleanup: Hapus referensi dari memory system (Garbage Collection Trigger)
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]

        smf.printf("Plugin unloaded completely =>", plugin_name)
        smf.printd("Plugin unloaded completely", plugin_name, level="INFO")

    def get(self, plugin_name):
        """Dipanggil oleh caller untuk mendapatkan plugin."""
        if plugin_name not in self.registry:
            smf.printd(
                "Caller requested inactive/missing plugin", plugin_name, level="WARN"
            )
            return NullPlugin(plugin_name)
        return self.registry[plugin_name]


# Plugin registration
registry = PluginManager()
