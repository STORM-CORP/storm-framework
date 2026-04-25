# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import functools
from typing import Any, Tuple
import smf


class SilentAbsorber:
    """
    Objek 'Black Hole' (Universal Dummy).
    Mencegah crash dari TypeError (None is not callable) atau AttributeError berantai.
    """

    def __init__(self, plugin_name: str, attr_name: str):
        self._plugin_name = plugin_name
        self._attr_name = attr_name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        smf.printd(
            f"Dead Call Absorbed [{self._plugin_name}]",
            f"Attempted to call missing/failed '{self._attr_name}'.",
            level="WARN",
        )
        return None

    def __getattr__(self, name: str) -> "SilentAbsorber":
        # Jika diakses berantai: plugin.objek_hilang.fungsi_lain()
        return SilentAbsorber(self._plugin_name, f"{self._attr_name}.{name}")

    # Magic methods untuk toleransi operasi dasar
    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:
        """Sangat penting untuk debugging via REPL atau log."""
        return f"<SilentAbsorber({self._plugin_name}.{self._attr_name})>"


class SafePluginProxy:
    """
    Membungkus instance plugin asli.
    Menangkap error saat runtime, memelihara metadata, dan meneruskan mutasi state.
    """

    # Menggunakan __slots__ tidak mungkin karena kita butuh __dict__ dinamis untuk setattr bypass,
    # tapi kita mendefinisikan field internal yang tidak boleh diteruskan ke instance asli.
    _INTERNAL_FIELDS: Tuple[str, ...] = ("_plugin_name", "_instance", "_method_cache")

    def __init__(self, plugin_name: str, instance: Any):
        # Menggunakan super().__setattr__ untuk menghindari infinite recursion
        # pada custom __setattr__ di bawah.
        super().__setattr__("_plugin_name", plugin_name)
        super().__setattr__("_instance", instance)

        # [OPTIMASI 1]: Caching untuk Method Wrapper (Mencegah Memory Leak & CPU Overhead)
        super().__setattr__("_method_cache", {})

    def __getattr__(self, name: str) -> Any:
        # 1. Cek Cache (O(1) Lookup) agar tidak me-rebuild wrapper secara repetitif
        if name in self._method_cache:
            return self._method_cache[name]

        try:
            # Ambil atribut/method asli dari instance
            attr = getattr(self._instance, name)

            if callable(attr):
                # Buat wrapper penangkap error
                @functools.wraps(attr)
                def safe_method_wrapper(*args: Any, **kwargs: Any) -> Any:
                    try:
                        return attr(*args, **kwargs)
                    except Exception as e:
                        smf.printd(
                            f"Plugin Runtime Crash [{self._plugin_name}]",
                            f"Method '{name}' failed: {e}",
                            level="ERROR",
                        )
                        return None

                # Simpan ke cache sebelum dikembalikan
                self._method_cache[name] = safe_method_wrapper
                return safe_method_wrapper

            # Jika atribut berupa properti statis, langsung kembalikan
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

    def __setattr__(self, name: str, value: Any) -> None:
        """
        [OPTIMASI 2]: Delegasi Mutasi State.
        Memastikan jika framework melakukan `plugin.state = X`,
        nilai tersebut masuk ke instance asli, bukan menempel di Proxy.
        """
        if name in self._INTERNAL_FIELDS:
            super().__setattr__(name, value)
        else:
            setattr(self._instance, name, value)

    def __delattr__(self, name: str) -> None:
        """Menjamin sinkronisasi jika atribut dihapus dari luar."""
        if name in self._INTERNAL_FIELDS:
            super().__delattr__(name)
        else:
            delattr(self._instance, name)

            # Jika method/property dihapus, bersihkan juga dari cache (Invalidasi)
            if name in self._method_cache:
                del self._method_cache[name]


class NullPlugin:
    """
    Null Object Pattern.
    Menyerap semua pemanggilan jika plugin gagal dimuat tanpa menyebabkan exception.
    """

    def __init__(self, plugin_name: str):
        self._plugin_name = plugin_name

    def __getattr__(self, name: str) -> SilentAbsorber:
        return SilentAbsorber(self._plugin_name, name)
