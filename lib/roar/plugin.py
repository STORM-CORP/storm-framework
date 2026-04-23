# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
from .plugin.manager import PluginManager


class StormFrameworkPlugin:
    """
    The main facade of the framework.
    Manages the lifecycle of internal components such as the PluginManager.
    """

    def __init__(self):
        self.plugins = PluginManager()
        self.is_running = False

    def start(self):
        """Plugin execution entry point."""

        # 1. Booting Plugins
        self.plugins.boot()

        # 2. Set status
        self.is_running = True

        # Internal system log
        smf.printd("System Plugin Running...", level="INFO")

    def stop(self):
        """Teardown / Graceful Shutdown."""

        # Cleanup logic
        self.is_running = False


# ==========================================
# SINGLETON & ENTRY POINT EKSEKUSI
# ==========================================

app = StormFrameworkPlugin()
