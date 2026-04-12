# Lokasi: plugin/

from apps.utility.plugin.utils_plugin import plugin

def examples():
    # Ambil objek pluginnya
    func = plugin("plugin_name")

    if func:
        # Sekarang kamu bisa akses apapun yang ada di dalam file plugin itu
        func.plugin_function()
