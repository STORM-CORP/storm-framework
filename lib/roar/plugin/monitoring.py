# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
from .safe import NullPlugin


class PluginMonitoring:
    """
    A mixin class to provide observability to PluginManager.
    This inheriting class must have the self.plugin_dir and self.registry attributes.
    """

    def list_available_on_disk(self) -> list:
        """Recursively scans the plugin folder for python files."""
        available = []
        # Make sure plugin_dir exists before scanning.
        if not os.path.exists(self.plugin_dir):
            return []

        for root, _, files in os.walk(self.plugin_dir):
            for file in files:
                # Filter: only .py and not dunder/private files
                if file.endswith(".py") and not file.startswith("__"):
                    available.append(file[:-3])

        return sorted(list(set(available)))  # Set to avoid path duplication

    def get_status_map(self) -> list[dict]:
        """
        Returns a complete state map of the plugin.
        """
        disk_plugins = self.list_available_on_disk()
        status_report = []

        for p_name in disk_plugins:
            status = "Non-Active"

            if p_name in self.registry:
                # Crash detection logic via NullPlugin
                if isinstance(self.registry[p_name], NullPlugin):
                    status = "CRASHED"
                else:
                    status = "ACTIVE"

            status_report.append({"name": p_name, "status": status})

        return status_report
