import time
import sys
import smf


def execute(options):
    # 1. Siapkan 10.000 data log raksasa
    total_logs = 10_000
    print(f"Menyiapkan payload {total_logs} baris log...")

    # Kita buat list berisi 10.000 string
    payload = [
        f"[LOG ENTRY {i}] System status nominal. Memory address: 0x00F{i}A"
        for i in range(total_logs)
    ]

    # =======================================================
    # TEST 1: STANDARD PYTHON PRINT
    # =======================================================
    print("\n--- MULAI TEST: PYTHON PRINT BAWAAN ---")
    time.sleep(1)  # Jeda agar CPU stabil

    start_py = time.perf_counter()
    # Membongkar 10.000 argumen ke dalam print() bawaan
    print(*payload, sep="\r", file=sys.stdout)
    end_py = time.perf_counter()
    time_py = end_py - start_py

    # =======================================================
    # TEST 2: STORM FRAMEWORK PRINT (RUST)
    # =======================================================
    print("\n--- MULAI TEST: STORM RUST PRINT ---")
    time.sleep(1)

    start_rust = time.perf_counter()
    # Membongkar 10.000 argumen ke dalam FFI Rust Anda
    smf.printf(*payload, sep="\r", file=sys.stdout, flush=True)
    end_rust = time.perf_counter()
    time_rust = end_rust - start_rust

    # =======================================================
    # HASIL ANALISIS
    # =======================================================
    print("\n" + "=" * 50)
    print("🏆 HASIL BENCHMARK (10.000 DATA)")
    print("=" * 50)
    print(f"Python Bawaan : {time_py:.6f} detik")
    print(f"Storm Rust    : {time_rust:.6f} detik")

    if time_rust < time_py:
        speedup = time_py / time_rust
        print(f"\n⚡ KESIMPULAN: Mesin Rust Anda {speedup:.2f}x LEBIH CEPAT!")
    else:
        print("\nKesimpulan: Ada bottleneck di tempat lain.")
