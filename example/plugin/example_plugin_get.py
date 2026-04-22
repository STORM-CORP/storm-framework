from lib.roar.plugin.manager import PluginManager

def run_external_logic():
    """Simulasi komponen framework lain yang membutuhkan plugin"""

    ex_plugin = PluginManager()
    # 1. Minta instance plugin dari manager (Inversion of Control)
    plugin = ex_plugin.get("demo_plug")
        
    # -- Skenario 1: Fungsi Berjalan Normal --
    # Jika plugin belum di-load, plugin.process_data akan ditangkap 
    # oleh SilentAbsorber dan me-return None tanpa error.
    hasil = plugin.process_data("Packet-01")
    if hasil:
        print(f"[Core] Hasil proses: {hasil}")

    # -- Skenario 2: Fungsi Memicu Crash (Runtime Error) --
    # Jika caller memanggil fungsi yang rusak, framework TETAP HIDUP.
    # Error (ZeroDivisionError) akan dikirim ke Rust logger, dan
    # method ini diam-diam me-return None.
    plugin.trigger_crash()
        
    # -- Skenario 3: Memanggil fungsi yang tidak pernah dibuat --
    # Caller berhalusinasi dan memanggil objek berantai yang tidak ada.
    # SilentAbsorber akan menyerap .database, .connect(), dan .fetch().
    # Tidak ada AttributeError maupun TypeError yang bocor ke thread utama.
    plugin.database.connect().fetch("SELECT *")
        
    print("[Core] Logika luar selesai dieksekusi dengan aman.")
      
