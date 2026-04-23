# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import json
from pathlib import Path
from typing import Set, Dict, Any
import smf
from rootmap import ROOT


class PluginStateStore:
    def __init__(self) -> None:
        # Konstruksi path menggunakan pathlib (Konsisten dengan modul lain)
        self.cachepath: Path = Path(ROOT) / "lib" / "smf" / "core" / "sf" / "cache" / "plugin-session"
        self.filepath: Path = self.cachepath / "plugin_cache.json"
        
        # Eksekusi setara dengan os.makedirs(..., exist_ok=True)
        self.cachepath.mkdir(parents=True, exist_ok=True)

    def load_active_plugins(self) -> Set[str]:
        """
        Memuat daftar plugin yang aktif dari storage.
        Kompleksitas: O(1) saat lookup (karena direturn sebagai Set).
        """
        if not self.filepath.exists():
            return set()
            
        try:
            # Operasi baca dioptimasi menggunakan pathlib.read_text
            # Explicit utf-8 untuk menghindari bug encoding di OS Windows
            data_text = self.filepath.read_text(encoding="utf-8")
            data: Dict[str, Any] = json.loads(data_text)
            
            return set(data.get("active_plugins", []))
            
        except json.JSONDecodeError as e:
            smf.printd("State Storage JSON Corrupted", str(e), level="ERROR")
            # Fallback ke set kosong jika korup, agar sistem tetap bisa boot
            return set()
        except Exception as e:
            smf.printd("State Storage Error", str(e), level="CRITICAL")
            return set()

    def save_active_plugins(self, active_plugins_set: Set[str]) -> None:
        """
        Menyimpan state plugin ke disk.
        Pola: Temp File -> Write -> Atomic Replace (OS Level).
        """
        temp_filepath = self.filepath.with_suffix(".tmp")
        
        try:
            # Konstruksi payload: Set harus dikonversi ke list karena JSON tidak mendukung Set
            payload = {"active_plugins": list(active_plugins_set)}
            
            # Tulis ke file temporary
            temp_filepath.write_text(json.dumps(payload, indent=4), encoding="utf-8")

            # OS-level atomic replace
            # Mengganti file asli dengan aman tanpa risiko data terpotong di tengah I/O
            temp_filepath.replace(self.filepath)

        except Exception as e:
            smf.printd("State Storage Save Error", str(e), level="ERROR")
        finally:
            # [OPTIMASI]: I/O Cleanup
            # Memastikan jika operasi gagal sebelum .replace() selesai, 
            # file .tmp tidak menjadi sampah di dalam storage
            if temp_filepath.exists():
                temp_filepath.unlink(missing_ok=True)
                
