# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from typing import Any, List

from .plugin import manager
from .plugin import monitoring
from .plugin import introspection


class StormAPI:
    """
    Antarmuka tunggal untuk REPL.
    User/CLI hanya boleh berinteraksi dengan class ini.
    """

    @staticmethod
    def show_plugins() -> List[dict]:
        """
        Perintah REPL: `show plugin`
        Menyambungkan manager ke monitoring.
        """
        # API mengambil 'State/Data' dari Manager...
        folder_plugin = manager.PLUGIN_DIR
        data_di_ram = manager.REGISTRY

        # ...lalu menyuntikkan data tersebut ke fungsi Monitoring.
        # Monitoring akan memprosesnya dan mengembalikan laporan.
        laporan = monitoring.get_status_map(folder_plugin, data_di_ram)

        return laporan

    @staticmethod
    def inspect_plugin(plugin_name: str) -> List[dict]:
        """
        Perintah REPL: `info <nama_plugin>`
        Menyambungkan manager ke introspection.
        """
        # API meminta spesifik 1 plugin dari Manager
        target_plugin = manager.get_plugin(plugin_name)

        # Melemparkan instance plugin tersebut ke fungsi Introspection (Pisau Bedah)
        manifest = introspection.get_plugin_manifest(target_plugin)

        return manifest

    @staticmethod
    def execute(plugin_name: str, payload: Any = None) -> Any:
        """Eksekusi tunggal plugin."""
        plugin = manager.get_plugin(plugin_name)
        if not plugin or isinstance(plugin, manager.NullPlugin):
            return f"[ERROR] Plugin '{plugin_name}' tidak dapat dieksekusi."

        action = getattr(plugin, "run", None)
        if callable(action):
            return action(payload)
        return f"[ERROR] Plugin {plugin_name} tidak memiliki fungsi 'run()'."


# Expose instance untuk di-import oleh file CLI/Terminal Anda
app = StormAPI()
