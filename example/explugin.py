# Lokasi: plugin/

from apps.utility.plugin.utils_plugin import plugin

# Ambil objek pluginnya
func = plugin("nama_plugin_kamu")

if func:
    # Sekarang kamu bisa akses apapun yang ada di dalam file plugin itu
    func.fungsi_apapun()
