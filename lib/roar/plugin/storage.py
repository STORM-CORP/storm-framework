# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import json
import os
import smf
from rootmap import ROOT


class PluginStateStore:
    def __init__(self):
        # Konstruksi path absolut
        self.cachepath = os.path.join(
            ROOT, "lib", "smf", "core", "sf", "cache", "plugin-session"
        )
        self.filepath = os.path.join(self.cachepath, "plugin_cache.json")
        os.makedirs(self.cachepath, exist_ok=True)

    def load_active_plugins(self):
        if not os.path.exists(self.filepath):
            return set()
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return set(data.get("active_plugins", []))
        except json.JSONDecodeError as e:
            smf.printd("State Storage JSON Corrupted", e, level="ERROR")
            return set()
        except Exception as e:
            smf.printd("State Storage Error", e, level="CRITICAL")
            return set()

    def save_active_plugins(self, active_plugins_set):
        try:
            # [KOREKSI 3]: Implementasi Atomic Write untuk mencegah korupsi data
            temp_filepath = f"{self.filepath}.tmp"

            with open(temp_filepath, "w") as f:
                json.dump({"active_plugins": list(active_plugins_set)}, f, indent=4)

            # OS-level atomic replace. Jika proses gagal sebelum baris ini,
            # file asli (plugin_cache.json) tidak akan rusak.
            os.replace(temp_filepath, self.filepath)

        except Exception as e:
            smf.printd("State Storage Save Error", e, level="ERROR")
