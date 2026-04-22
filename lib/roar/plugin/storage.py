import json
import os
import smf


class PluginStateStore:
    def __init__(self, filepath="plugin_cache.json"):
        self.filepath = filepath

    def load_active_plugins(self):
        if not os.path.exists(self.filepath):
            return set()
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return set(data.get("active_plugins", []))
        except Exception as e:
            smf.printd("State Storage Error", e, level="CRITICAL")
            return set()

    def save_active_plugins(self, active_plugins_set):
        try:
            with open(self.filepath, "w") as f:
                json.dump({"active_plugins": list(active_plugins_set)}, f, indent=4)
        except Exception as e:
            smf.printd("State Storage Save Error", e, level="ERROR")
