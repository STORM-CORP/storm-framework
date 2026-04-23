# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from typing import Any
from .plugin import manager


class StormAPI:
    """
    Facade idiot-proof untuk eksekusi perintah Storm.
    Tidak ada class inheritance, hanya pemanggilan fungsi murni ke mesin.
    """

    @staticmethod
    def execute(plugin_name: str, payload: Any = None) -> Any:
        """
        [ATURAN EMAS]: Satu fungsi untuk mengeksekusi semua plugin.
        Framework berasumsi setiap plugin murni fungsional dan memiliki fungsi 'run()'.
        """
        # Mengambil referensi dari memori manager
        plugin = manager.get_plugin(plugin_name)

        if not plugin:
            smf.printd(f"[ERROR] Plugin '{plugin_name}' is not active.")
            return

        # Sanitasi terpusat (contoh sederhana)
        clean_payload = str(payload).strip() if payload is not None else None

        # Introspeksi fungsional (Mencari fungsi run)
        action = getattr(plugin, "run", None)

        if callable(action):
            try:
                # Direct Dispatch Execution
                return action(clean_payload)
            except Exception as e:
                smf.printd(f"[CRITICAL] Crash on execution => {plugin_name}", e)
                return
        else:
            smf.printd(
                f"[ERROR] Plugin {plugin_name} violates contract. No functionality 'run()'."
            )
            return

    @staticmethod
    def trigger_event(event_name: str, *args, **kwargs) -> dict:
        """Menyiarkan sinyal ke semua plugin yang mendengarkan."""
        return manager.broadcast(event_name, *args, **kwargs)


# Instance statis untuk Caller
plugin = StormAPI()
