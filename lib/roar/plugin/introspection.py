# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import inspect
from .safe import NullPlugin


class PluginIntrospection:
    """
    Mixin class untuk memberikan kemampuan bedah plugin (Introspection).
    Asumsi: Class yang mewarisi ini memiliki method self.get().
    """

    def function(self, plugin_name: str) -> list[dict]:
        """
        Membongkar plugin untuk memetakan fungsi-fungsi publiknya.
        """
        # 1. Ambil plugin (otomatis lewat proxy jika manager sudah di-mix)
        plugin = self.get(plugin_name)

        # 2. Early Exit: Jika plugin tidak valid
        if isinstance(plugin, NullPlugin):
            return []

        # 3. Proxy Unwrapping
        # Mengambil instance asli di balik SafePluginProxy
        actual_instance = getattr(plugin, "_instance", plugin)
        manifest = []

        # 4. Scanning methods
        for name, func in inspect.getmembers(
            actual_instance, predicate=inspect.ismethod
        ):
            # Filter: Hanya fungsi publik (tanpa awalan _)
            if not name.startswith("_"):
                try:
                    sig = inspect.signature(func)
                    # Cleaning: Hapus 'self' agar tampilan di REPL bersih
                    params = str(sig).replace("(self, ", "(").replace("(self)", "()")

                    manifest.append({"action": name, "parameters": params})
                except Exception:
                    manifest.append({"action": name, "parameters": "(...)"})

        return manifest
