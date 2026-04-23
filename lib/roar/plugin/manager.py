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
from .introspection import PluginIntrospection


class PluginManager(PluginMonitoring, PluginIntrospection):

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

    
    def _trigger_hook(self, p_name: str, hook_name: str):
        """
        Mencari dan menjalankan fungsi lifecycle (hook) pada plugin jika tersedia.
        """
        plugin = self.get(p_name)
    
        # Mencari atribut fungsi berdasarkan nama (on_boot, on_shutdown, dll)
        # Jika tidak ada, getattr akan memberikan None
        hook = getattr(plugin, hook_name, None)

        if callable(hook):
            try:
                smf.printd("Lifecycle", f"Executing {hook_name} for {p_name}", level="DEBUG")
                hook() # Panggil tanpa argumen
                return True
            except Exception as e:
                smf.printd("Lifecycle", f"Failed {hook_name} on {p_name}: {e}", level="ERROR")
    
        return False
    

    def boot(self):
        """
        Standard boot sequence: Load -> Trigger on_boot.
        """
        active_list = list(self.active_plugins)
        smf.printd("Booting PluginManager", active_list, level="INFO")

        for p_name in active_list:
            # Load plugin menggunakan public method agar aman (pake Proxy)
            if self.load(p_name):
                # Cukup panggil dispatcher untuk hook 'on_boot'
                self._trigger_hook(p_name, "sync_modules")
            
    
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
            smf.printf(
                f"{CC.GREEN}[✓] Plugin loaded successfully =>{CC.RESET}", plugin_name
            )
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
