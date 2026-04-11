import os
import importlib.util
from rootmap import ROOT

class PluginEngine:
    def __init__(self):
        self.plugin_dir = os.path.join(ROOT, "plugin")
        self.registry = {} # Tempat simpan plugin yang sudah ter-load

    def start_loader(self):
        """Dijalankan sekali saat framework pertama kali dibuka"""
        for root, dirs, files in os.walk(self.plugin_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    path = os.path.join(root, file)
                    name = file[:-3] # Contoh: 'port'

                    # 1. Load filenya ke memori secara dinamis
                    module = self._dynamic_import(name, path)

                    # 2. Tanya ke plugin: "Kamu mau auto-start ga?"
                    if hasattr(module, 'plugin'):
                        try:
                            response = module.plugin({"event": "startup"})
                        except Exception as e:
                            print(f"[!] ERROR PLUGIN => {e}")

                        # Simpan di registry agar bisa dipanggil nanti lewat command
                        self.registry[name] = module

                        # 3. Jika plugin minta auto_start, langsung jalankan
                        if response and response.get("auto_start"):
                            module.plugin({"event": "command"})

    def _dynamic_import(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_command(self, name_plugin):
        """Dijalankan saat user ngetik: plugin <name_plugin>"""
        if name_plugin in self.registry:
            module = self.registry[name_plugin]

            # Jalankan dengan event 'command'
            module.plugin({"event": "command"})
        else:
            print(f"[-] Plugin => {name_plugin} > not found.")
