# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import inspect
from typing import List, Any, TypedDict, Optional
from .safe import NullPlugin


class PluginMethodManifest(TypedDict):
    """Kontrak struktur data hasil introspeksi."""

    action: str
    parameters: str
    description: Optional[str]


def get_plugin_manifest(plugin_instance: Any) -> List[PluginMethodManifest]:
    """
    Fungsi bedah murni.
    Menerima instance plugin apa saja (menembus proxy), lalu memetakan fungsi publiknya.
    """
    # 1. Early Exit: Proteksi null object pattern
    if isinstance(plugin_instance, NullPlugin) or not plugin_instance:
        return []

    # 2. Proxy Unwrapping: Tembus lapisan isolasi ke modul/instance asli
    actual_instance = getattr(plugin_instance, "_instance", plugin_instance)
    manifest: List[PluginMethodManifest] = []

    # 3. Scanning: Karena plugin tanpa class, kita mencari murni 'function'
    for name, func in inspect.getmembers(actual_instance, predicate=inspect.isfunction):

        # Abaikan private/protected/dunder functions
        if name.startswith("_"):
            continue

        # 4. Resolusi Signature (Jauh lebih bersih karena bebas 'self')
        try:
            sig = inspect.signature(func)
            clean_params = str(sig)
        except ValueError:
            # Fallback jika inspect gagal membongkar (C-extensions/built-ins)
            clean_params = "(...)"

        # 5. Ekstraksi Metadata & Penyatuan Data
        manifest.append(
            {
                "action": name,
                "parameters": clean_params,
                "description": inspect.getdoc(func),
            }
        )

    return manifest
