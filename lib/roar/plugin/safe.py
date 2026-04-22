# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import functools
import smf


class SilentAbsorber:
    """
    Objek 'Black Hole' (Universal Dummy).
    Mencegah crash dari TypeError (None is not callable) atau AttributeError berantai.
    """

    def __init__(self, plugin_name, attr_name):
        self._plugin_name = plugin_name
        self._attr_name = attr_name

    def __call__(self, *args, **kwargs):
        smf.printd(
            f"Dead Call Absorbed [{self._plugin_name}]",
            f"Attempted to call missing/failed '{self._attr_name}'.",
            level="WARN",
        )
        return None

    def __getattr__(self, name):
        # Jika diakses berantai: plugin.objek_hilang.fungsi_lain()
        # Mengembalikan instance absorber baru untuk rantai selanjutnya
        return SilentAbsorber(self._plugin_name, f"{self._attr_name}.{name}")

    # Magic methods untuk toleransi tipe data (mencegah crash pada if/str logic)
    def __bool__(self):
        return False  # Jika framework mengecek: if plugin.fitur_x:

    def __str__(self):
        return ""


class SafePluginProxy:
    """Membungkus instance plugin asli. Menangkap error saat runtime dan memelihara metadata."""

    def __init__(self, plugin_name, instance):
        self._plugin_name = plugin_name
        self._instance = instance

    def __getattr__(self, name):
        try:
            # Ambil atribut/method asli dari instance
            attr = getattr(self._instance, name)

            if callable(attr):
                # [OPTIMASI 1]: Pertahankan metadata fungsi asli (signature, docstring)
                @functools.wraps(attr)
                def safe_method_wrapper(*args, **kwargs):
                    try:
                        return attr(*args, **kwargs)
                    except Exception as e:
                        smf.printd(
                            f"Plugin Runtime Crash [{self._plugin_name}]",
                            f"Method '{name}' failed: ",
                            e,
                            level="ERROR",
                        )
                        return None

                return safe_method_wrapper

            # Jika atribut berupa properti statis (bukan method), kembalikan aslinya
            return attr

        except AttributeError:
            smf.printd(
                f"Plugin Attribute Missing [{self._plugin_name}]",
                f"Missing attribute '{name}' accessed.",
                level="WARN",
            )
            return SilentAbsorber(self._plugin_name, name)

        except Exception as e:
            smf.printd(f"Unexpected Error [{self._plugin_name}]", e, level="CRITICAL")
            return SilentAbsorber(self._plugin_name, name)


class NullPlugin:
    """
    Null Object Pattern.
    Menyerap semua pemanggilan jika plugin gagal dimuat tanpa menyebabkan exception.
    """

    def __init__(self, plugin_name):
        self._plugin_name = plugin_name

    def __getattr__(self, name):
        # Menggunakan SilentAbsorber yang sama agar logic terpusat
        return SilentAbsorber(self._plugin_name, name)
