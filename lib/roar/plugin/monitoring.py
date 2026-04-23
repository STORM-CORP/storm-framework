# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from pathlib import Path
from typing import List, Dict, Any, Protocol, TypedDict, Literal
from .safe import NullPlugin

# 1. Strict Typing untuk Status
# Mengunci nilai string agar IDE bisa menangkap jika ada typo (contoh: "ACTIF")
PluginStatus = Literal["ACTIVE", "INACTIVE", "CRASHED", "ORPHANED"]


class PluginStatusReport(TypedDict):
    """Kontrak struktur data metrik plugin."""

    name: str
    status: PluginStatus
    is_package: bool


class MonitoringProvider(Protocol):
    """
    Interface/Protocol untuk Type Checker.
    Menjamin class host memiliki attribute plugin_dir (berupa Path) dan registry.
    """

    plugin_dir: Path
    registry: Dict[str, Any]


class PluginMonitoring:
    """
    Mixin class untuk memberikan observability pada PluginManager.
    """

    def list_available_on_disk(self: MonitoringProvider) -> Dict[str, bool]:
        """
        Scans plugin folder efficiently.
        Mengembalikan dictionary O(1) lookup: {plugin_name: is_package_bool}
        """
        available: Dict[str, bool] = {}

        if not getattr(self, "plugin_dir", None) or not self.plugin_dir.exists():
            return available

        # Iterasi efisien menggunakan rglob (mencakup sub-direktori)
        for path in self.plugin_dir.rglob("*.py"):
            # Abaikan cache atau file tersembunyi
            if "__pycache__" in path.parts or path.name.startswith("."):
                continue

            # Dukungan Arsitektur 1: Package Based
            if path.name == "__init__.py":
                plugin_name = path.parent.name
                available[plugin_name] = True

            # Dukungan Arsitektur 2: Single File
            elif not path.name.startswith("__"):
                plugin_name = path.stem
                if plugin_name not in available:
                    available[plugin_name] = False

        return available

    def get_status_map(self: MonitoringProvider) -> List[PluginStatusReport]:
        """
        Melakukan rekonsiliasi state antara Memory (RAM) vs Physical Disk.
        """
        disk_plugins = self.list_available_on_disk()
        status_report: List[PluginStatusReport] = []

        # Reference ke memory state (O(1) dictionary view)
        loaded_plugins = getattr(self, "registry", {})

        # Fase 1: Pemetaan dari sudut pandang Physical Disk
        for p_name, is_package in disk_plugins.items():
            status: PluginStatus = "INACTIVE"

            if p_name in loaded_plugins:
                # Cek apakah object-nya NullPlugin (Crashing at Load)
                if isinstance(loaded_plugins[p_name], NullPlugin):
                    status = "CRASHED"
                else:
                    status = "ACTIVE"

            status_report.append(
                {"name": p_name, "status": status, "is_package": is_package}
            )

        # Fase 2: Deteksi "Orphaned / Zombie Plugins"
        # Kasus dimana plugin ada di Memory, tapi filenya sudah dihapus dari Disk
        for p_name, instance in loaded_plugins.items():
            if p_name not in disk_plugins:
                status: PluginStatus = "ORPHANED"

                # Walaupun orphaned, bisa jadi dia memang sudah crash
                if isinstance(instance, NullPlugin):
                    status = "CRASHED"

                status_report.append(
                    {
                        "name": p_name,
                        "status": status,
                        "is_package": False,  # Tidak diketahui secara pasti karena file sudah hilang
                    }
                )

        return status_report
