# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import inspect
from typing import List, Any, Protocol, TypedDict, Optional
from .safe import NullPlugin


class PluginMethodManifest(TypedDict):
    """Kontrak struktur data hasil introspeksi."""

    action: str
    parameters: str
    description: Optional[str]


class PluginProvider(Protocol):
    """
    Protocol / Interface abstrak untuk memuaskan Static Type Checker.
    Ini memberitahu IDE: "Mixin ini akan digabung dengan class yang memiliki method get()".
    """

    def get(self, plugin_name: str) -> Any: ...


class PluginIntrospection:
    """
    Mixin class untuk memberikan kemampuan bedah plugin (Introspection).
    Memerlukan host class yang mengimplementasikan PluginProvider.
    """

    def get_plugin_manifest(
        self: PluginProvider, plugin_name: str
    ) -> List[PluginMethodManifest]:
        """
        Membongkar plugin untuk memetakan fungsi-fungsi publik beserta metadata.
        """
        # 1. Ambil plugin melalui method host class
        plugin = self.get(plugin_name)

        # 2. Early Exit: Proteksi null object pattern
        if isinstance(plugin, NullPlugin):
            return []

        # 3. Proxy Unwrapping: Tembus lapisan isolasi ke instance asli
        actual_instance = getattr(plugin, "_instance", plugin)
        manifest: List[PluginMethodManifest] = []

        # 4. Scanning methods: Ambil member yang murni berupa method
        for name, func in inspect.getmembers(
            actual_instance, predicate=inspect.ismethod
        ):

            # Abaikan private/protected/dunder methods
            if name.startswith("_"):
                continue

            # Resolusi Signature & Pembersihan 'self' secara struktural (bukan regex/string)
            try:
                sig = inspect.signature(func)
                params_list = list(sig.parameters.values())

                # Jika parameter pertama bernama 'self', kita buat signature baru tanpanya
                if params_list and params_list[0].name == "self":
                    new_sig = sig.replace(parameters=params_list[1:])
                    clean_params = str(new_sig)
                else:
                    clean_params = str(sig)

            except ValueError:
                # Fallback jika inspect gagal membongkar (biasanya terjadi pada C-extension/built-ins)
                clean_params = "(...)"

            # Ekstraksi Metadata
            docstring = inspect.getdoc(func)

            # 5. Penyatuan Data ke dalam Kontrak TypedDict
            manifest.append(
                {"action": name, "parameters": clean_params, "description": docstring}
            )

        return manifest
