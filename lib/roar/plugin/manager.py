# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import importlib
import sys
import smf
import os

from .storage import PluginStateStore
from .safe import SafePluginProxy, NullPlugin


class PluginManager:
    def __init__(self):
        self.plugin_dir = os.path.join(ROOT, "plugin")
        self.registry = {}
        self.store = PluginStateStore()
        self.active_plugins = self.store.load_active_plugins()

        # Daftarkan direktori ke sys.path agar python bisa meng-importnya
        if self.plugin_dir not in sys.path:
            sys.path.insert(0, self.plugin_dir)

    def boot(self):
        """Dijalankan saat framework start, me-load semua plugin yang tersimpan di cache."""
        smf.printd("Booting PluginManager", list(self.active_plugins), level="INFO")
        plugins_to_load = list(self.active_plugins)
        for p_name in plugins_to_load:
            self._load_module(p_name)

    def _load_module(self, plugin_name):
        try:
            smf.printd("Loading module", plugin_name, level="DEBUG")

            # Jika sudah ada di sys.modules, paksa reload agar kode terbaru terbaca
            if plugin_name in sys.modules:
                module = importlib.reload(sys.modules[plugin_name])
            else:
                module = importlib.import_module(plugin_name)

            # Asumsi: Setiap plugin memiliki class bernama 'Plugin' sebagai entry point
            if not hasattr(module, "Plugin"):
                raise AttributeError(
                    f"Module {plugin_name} is missing the main 'Plugin' class."
                )

            instance = module.Plugin()
            safe_instance = SafePluginProxy(plugin_name, instance)
            self.registry[plugin_name] = safe_instance

            smf.printd("Plugin loaded successfully", plugin_name, level="INFO")
            return True

        except Exception as e:
            # Isolasi kegagalan pada level load (SyntaxError, ImportError, dll)
            smf.printd(
                f"Failed to load plugin [{plugin_name}]", str(e), level="CRITICAL"
            )
            # Tandai plugin ini di registry dengan NullPlugin
            self.registry[plugin_name] = NullPlugin(plugin_name)
            return False

    def load(self, plugin_name):
        """Command handler untuk me-load plugin baru."""
        success = self._load_module(plugin_name)
        if success:
            self.active_plugins.add(plugin_name)
            self.store.save_active_plugins(self.active_plugins)
        return success

    def unload(self, plugin_name):
        """Command handler untuk mematikan plugin."""
        if plugin_name in self.registry:
            del self.registry[plugin_name]
            smf.printd("Plugin instances destroyed", plugin_name, level="DEBUG")

        if plugin_name in self.active_plugins:
            self.active_plugins.remove(plugin_name)
            self.store.save_active_plugins(self.active_plugins)

        # Hapus referensi dari memory system agar bersih sepenuhnya
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]

        smf.printd("Plugin unloaded completely", plugin_name, level="INFO")

    def get(self, plugin_name):
        """Dipanggil oleh caller untuk mendapatkan plugin."""
        if plugin_name not in self.registry:
            smf.printd("Caller requested inactive plugin", plugin_name, level="WARN")
            return NullPlugin(plugin_name)
        return self.registry[plugin_name]
