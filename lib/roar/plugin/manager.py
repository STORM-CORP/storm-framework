# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import importlib.util
import sys
import smf
import os

from apps.utility.colors import CC
from rootmap import ROOT
from .storage import PluginStateStore
from .safe import SafePluginProxy, NullPlugin
from .monitoring import PluginMonitoring


class PluginManager(PluginMonitoring):
    def __init__(self):
        self.plugin_dir = os.path.join(ROOT, "plugin")
        self.registry = {}
        self.store = PluginStateStore()
        self.active_plugins = self.store.load_active_plugins()

        # Guaranteed existence of root plugin directory
        os.makedirs(self.plugin_dir, exist_ok=True)

    def _resolve_plugin_path(self, plugin_name):
        """
        O(N) Directory Traversal.
        Searches for plugins recursively in self.plugin_dir.
        Supports 2 plugin architectures:
        1. Single File   : /subfolder/pluginname.py
        2. Package Based : /subfolder/pluginname/__init__.py
        """
        for root, dirs, files in os.walk(self.plugin_dir):
            # Single file (pluginname.py)
            target_file = f"{plugin_name}.py"
            if target_file in files:
                return os.path.join(root, target_file)

            # Directory based (pluginname/__init__.py)
            if os.path.basename(root) == plugin_name and "__init__.py" in files:
                return os.path.join(root, "__init__.py")

        return None

    def boot(self):
        """
        Runs when the framework starts,
        loads all plugins stored in the cache.
        """
        smf.printd("Booting PluginManager", list(self.active_plugins), level="INFO")

        # Iterate over copy(list) so that modifications
        # to the set do not trigger a RuntimeError
        for p_name in list(self.active_plugins):
            self._load_module(p_name)

    def _load_module(self, plugin_name):
        try:
            smf.printd("Resolving module path", plugin_name, level="DEBUG")

            # Path Resolution
            plugin_path = self._resolve_plugin_path(plugin_name)
            if not plugin_path:
                raise FileNotFoundError(
                    f"Plugin '{plugin_name}' not found in {self.plugin_dir} or its subdirectories."
                )

            # Low-level Module Specification loading (Prevents sys.path pollution)
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot create module spec for {plugin_path}")

            # Instance Module Memory Allocation
            module = importlib.util.module_from_spec(spec)

            # Register to sys.modules (Needed if the plugin does relative imports)
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
            smf.printf("Failed to load plugin =>", plugin_name)
            smf.printd(f"Failed to load plugin [{plugin_name}]", e, level="CRITICAL")
            self.registry[plugin_name] = NullPlugin(plugin_name)

            # Remove from sys.modules if load fails partially (Clean state)
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]

            return False

    def load(self, plugin_name):
        """Command handler to load new plugins."""
        # If we reload, we first delete it from memory so that the interpreter can
        # forced to read the latest physical file (replacing importlib.reload)
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]

        success = self._load_module(plugin_name)
        if success:
            self.active_plugins.add(plugin_name)
            self.store.save_active_plugins(self.active_plugins)
            smf.printf("Plugin loaded successfully =>", plugin_name)
        return success

    def unload(self, plugin_name):
        """Command handler to explicitly disable plugins."""

        # Target initialization (Strict Match)
        # We immediately check the registry for efficiency.
        if plugin_name in self.registry:
            # Delete instance from registry (RAM)
            del self.registry[plugin_name]
            smf.printd("Plugin instance destroyed", plugin_name, level="DEBUG")

            # Update Persistence (To prevent auto-load on restart)
            if plugin_name in self.active_plugins:
                self.active_plugins.remove(plugin_name)
                self.store.save_active_plugins(self.active_plugins)

            # Hard Cleanup (Memory Cache Python)
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]

            # Feedback Success
            smf.printf(
                f"{CC.GREEN}[✓] Plugin unloaded completely =>{CC.RESET}", plugin_name
            )
            smf.printd("Unloaded", plugin_name, level="INFO")
            return True

        # If not found in the registry
        else:
            smf.printf(f"{CC.YELLOW}[!] Plugin not found =>{CC.RESET}", plugin_name)
            smf.printd("Unload failed plugin not found.", plugin_name, level="WARN")
            return False

    def get(self, plugin_name):
        """Called by caller to get plugin."""
        if plugin_name not in self.registry:
            smf.printd(
                "Caller requested inactive/missing plugin", plugin_name, level="WARN"
            )
            return NullPlugin(plugin_name)
        return self.registry[plugin_name]


# Plugin registration
registry = PluginManager()
