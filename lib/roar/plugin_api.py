# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from typing import Any, List, Dict

from .plugin import manager
from .plugin import monitoring
from .plugin import introspection


class StormAPI:
    """
    Single interface for REPL.
    The user/CLI may only interact with this class.
    """

    @staticmethod
    def boot() -> None:
        return manager.boot()

    @staticmethod
    def load(plugin_name: str) -> bool:
        return manager.load(plugin_name)

    @staticmethod
    def unload(plugin_name: str) -> bool:
        return manager.unload(plugin_name)

    @staticmethod
    def broadcast(event_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return manager.broadcast(event_name, *args, **kwargs)

    @staticmethod
    def monitor() -> List[dict]:
        """
        Perintah REPL: `show plugin`
        Menyambungkan manager ke monitoring.
        """
        # API mengambil 'State/Data' dari Manager...
        pluginpath = manager.PLUGIN_DIR
        data = manager.REGISTRY

        # ...lalu menyuntikkan data tersebut ke fungsi Monitoring.
        # Monitoring akan memprosesnya dan mengembalikan laporan.
        laporan = monitoring.get_status_map(pluginpath, data)

        return laporan

    @staticmethod
    def inspect(plugin_name: str) -> List[dict]:
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
            return f"[ERROR] Plugin '{plugin_name}' could not be executed."

        action = getattr(plugin, "run", None)
        if callable(action):
            return action(payload)
        return f"[ERROR] Plugin {plugin_name} has no function 'run()'."


# Expose instance untuk di-import oleh file CLI/Terminal Anda
plugin = StormAPI()
