# -- https://github.com/StormWorld0/storm-framework
import os
from .safe import NullPlugin


class PluginMonitoring:
    """
    Mixin class untuk memberikan kemampuan observasi pada PluginManager.
    Asumsi: Class yang mewarisi ini harus memiliki atribut self.plugin_dir dan self.registry.
    """

    def list_available_on_disk(self) -> list:
        """Men-scan folder plugin secara rekursif untuk mencari file .py"""
        available = []
        # Pastikan plugin_dir ada sebelum scan
        if not os.path.exists(self.plugin_dir):
            return []

        for root, _, files in os.walk(self.plugin_dir):
            for file in files:
                # Filter: hanya .py dan bukan dunder/private files
                if file.endswith(".py") and not file.startswith("__"):
                    available.append(file[:-3])

        return sorted(list(set(available)))  # Set untuk menghindari duplikasi path

    def get_status_map(self) -> list[dict]:
        """
        Mengembalikan peta status lengkap plugin.
        """
        disk_plugins = self.list_available_on_disk()
        status_report = []

        for p_name in disk_plugins:
            status = "Non-Active"

            if p_name in self.registry:
                # Logika deteksi Crash lewat NullPlugin
                if isinstance(self.registry[p_name], NullPlugin):
                    status = "CRASHED"
                else:
                    status = "ACTIVE"

            status_report.append({"name": p_name, "status": status})

        return status_report
