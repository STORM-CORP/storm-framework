import smf


class SafePluginProxy:
    """Membungkus instance plugin asli. Menangkap error saat runtime."""

    def __init__(self, plugin_name, instance):
        self._plugin_name = plugin_name
        self._instance = instance

    def __getattr__(self, name):
        try:
            attr = getattr(self._instance, name)
            if callable(attr):

                def safe_method_wrapper(*args, **kwargs):
                    try:
                        return attr(*args, **kwargs)
                    except Exception as e:
                        # Tangkap crash runtime di dalam method plugin
                        smf.printd(
                            f"Plugin Runtime Crash [{self._plugin_name}]",
                            f"Method '{name}' failed: {str(e)}",
                            level="ERROR",
                        )
                        return None  # Kembalikan None agar caller tidak crash

                return safe_method_wrapper
            return attr
        except AttributeError as e:
            # Jika caller memanggil properti/method yang tidak ada di plugin
            smf.printd(
                f"Plugin Attribute Error [{self._plugin_name}]",
                f"Missing attribute '{name}'",
                level="WARN",
            )
            return None
        except Exception as e:
            smf.printd(
                f"Unexpected Error [{self._plugin_name}]", str(e), level="CRITICAL"
            )
            return None


class NullPlugin:
    """
    Null Object Pattern.
    Dikembalikan ke caller jika plugin gagal di-load (error syntax/tidak ada).
    Menyerap semua pemanggilan tanpa menyebabkan exception.
    """

    def __init__(self, plugin_name):
        self._plugin_name = plugin_name

    def __getattr__(self, name):
        def silent_absorber(*args, **kwargs):
            smf.printd(
                f"Dead Call Absorbed [{self._plugin_name}]",
                f"Attempted to call '{name}' on a failed/unloaded plugin.",
                level="WARN",
            )
            return None

        return silent_absorber
