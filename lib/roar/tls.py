import ctypes
import os
import smf
from .callbin.calling import call_bin


lib = call_bin("libstls.so")

# 2. Muat mesin Rust ke dalam memori Python
try:
    _engine = ctypes.CDLL(lib)
    
    # Daftarkan parameter memori (agar tidak terjadi memory leak/segfault)
    _engine.storm_fetch.argtypes = [ctypes.c_char_p]
    _engine.storm_fetch.restype = ctypes.c_void_p
    _engine.storm_free_string.argtypes = [ctypes.c_void_p]
except OSError as e:
    smf.printd("Failed to load STLS", e, level="ERROR")
    raise RuntimeError(f"Runtime error loading STLS!")

# 3. Buat API publik yang bersih
def get(url: str) -> str:
    """
    Melakukan HTTP GET request menggunakan Rust BoringSSL + H2 Evasion Engine.
    """
    # Ubah string Python ke string bahasa C (bytes)
    c_url = url.encode('utf-8')
    
    # Lempar ke STLS! (Proses asinkron tokio terjadi di dalam sini)
    ptr = _engine.storm_fetch(c_url)
    
    if not ptr:
        smf.printd("Error from internal STLS", ptr, level="DEBUG")
        raise Exception("STLS internal failure (Null Pointer).")
        
    try:
        # Tarik hasilnya dari memori C ke memori Python
        result = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf-8')
        return result
    finally:
        # BERSIHKAN MEMORI (Sangat krusial!)
        _engine.storm_free_string(ptr)
