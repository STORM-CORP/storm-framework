### MAINTENANCE ###
###_____________###
import os
import smf
import json
import ctypes
import inspect
import subprocess
import importlib.util
from rootmap import ROOT


class PluginEngine:
    def __init__(self):
        # 1. Tentukan path folder plugin secara dinamis via rootmap
        self.plugin_dir = os.path.join(ROOT, "plugin")

        # 2. Registry Memori (The Hooks)
        # python_hooks: menyimpan objek fungsi dari file .py
        # binary_hooks: menyimpan path file biner executable
        # shared_hooks: menyimpan path file .so atau .dll
        self.python_hooks = {}
        self.binary_hooks = []
        self.shared_hooks = []

    def load_plugin(self):
        """
        Dijalankan HANYA SEKALI saat startup Storm.
        Melakukan recursive scanning ke seluruh folder plugin.
        """
        if not os.path.exists(self.plugin_dir):
            smf.printf(f"[!] Folder plugin tidak ditemukan di: {self.plugin_dir}")
            return

        for root, dirs, files in os.walk(self.plugin_dir):
            for filename in files:
                file_path = os.path.join(root, filename)

                # --- A. DETEKSI PLUGIN PYTHON ---
                if filename.endswith(".py") and filename != "__init__.py":
                    self._load_python(file_path)

                # --- B. DETEKSI SHARED LIBRARY (C/RUST/GO) ---
                elif filename.endswith((".so", ".dll")):
                    self.shared_hooks.append(file_path)

                # --- C. DETEKSI STANDALONE BINARY ---
                # Cek apakah file memiliki izin eksekusi (Linux/Mac)
                elif os.access(file_path, os.X_OK) and not os.path.isdir(file_path):
                    self.binary_hooks.append(file_path)

        smf.printf(
            f"[*] Plugin Engine: {len(self.python_hooks)} Py-Hooks, "
            f"{len(self.shared_hooks)} Shared, {len(self.binary_hooks)} Binaries loaded."
        )

    def _load_python(self, file_path):
        """Membedah file Python dan mengambil fungsi 'on_' ke RAM"""
        # Buat namespace unik berdasarkan path relatif agar tidak bentrok
        rel_path = os.path.relpath(file_path, ROOT)
        module_name = f"storm.plugin.{rel_path.replace(os.sep, '.').replace('.py', '')}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Introspeksi fungsi yang diawali 'on_'
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and name.startswith("on_"):
                    if name not in self.python_hooks:
                        self.python_hooks[name] = []
                    self.python_hooks[name].append(obj)
        except Exception as e:
            smf.printf(f"[!] Gagal load plugin Python {file_path} =>", e)

    def run_plugin(self, event_name, context):
        """
        Eksekusi Lintas Bahasa (IPC & RAM).
        Inilah yang dipanggil oleh Core Storm di runtime.
        """
        # Konversi context (dict) ke JSON untuk komunikasi dengan biner
        payload_json = json.dumps(context)

        # --- 1. EKSEKUSI PYTHON (RAM - Super Fast) ---
        if event_name in self.python_hooks:
            for func in self.python_hooks[event_name]:
                try:
                    # Python bisa langsung merubah dict context karena pass-by-reference
                    func(context)
                except Exception as e:
                    smf.printf(f"[!] Python Plugin Error [{event_name}] =>", e)

        # --- 2. EKSEKUSI SHARED LIBRARY (.so / .dll) ---
        for lib_path in self.shared_hooks:
            try:
                lib = ctypes.CDLL(lib_path)
                # Syarat: Biner harus punya fungsi 'storm_hook' sebagai entry point
                if hasattr(lib, "storm_hook"):
                    # C-ABI: Kirim event_name dan json payload
                    lib.storm_hook(event_name.encode(), payload_json.encode())
            except Exception as e:
                pass  # Silently skip jika biner tidak kompatibel

        # --- 3. EKSEKUSI STANDALONE BINARY (IPC via STDIN/STDOUT) ---
        for bin_path in self.binary_hooks:
            try:
                # Menjalankan biner sebagai subprocess
                # Biner menerima event_name sebagai argumen dan context sebagai STDIN
                process = subprocess.run(
                    [bin_path, event_name],
                    input=payload_json,
                    capture_output=True,
                    text=True,
                    timeout=5,  # Hindari plugin biner yang 'hang'
                )

                # Jika biner memberikan output JSON, update context asli Storm
                if process.stdout.strip():
                    updated_data = json.loads(process.stdout)
                    context.update(updated_data)
            except Exception as e:
                smf.printf(f"[!] Binary Plugin Error [{os.path.basename(bin_path)}] =>", e)


# --- CONTOH INTEGRASI DI CORE STORM ---
"""
# 1. Di startup Storm:
from core.plugin_engine import PluginEngine
storm_plugins = PluginEngine()
storm_plugins.load_plugin()

# 2. Di runtime (misal saat modul auxiliary mau jalan):
options = {"RHOST": "127.0.0.1", "PORT": 80}
storm_plugins.run_plugin("on_pre_execute", options)
"""
