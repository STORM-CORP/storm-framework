import time
import sys
import smf


def execute(options):
    # 1. Prepare 10,000 giant log data
    total_logs = 10_000
    print(f"Preparing the payload {total_logs} log lines...")

    # Create a list containing 10,000 strings
    payload = [
        f"[LOG ENTRY {i}] System status nominal. Memory address: 0x00F{i}A"
        for i in range(total_logs)
    ]

    # =======================================================
    # TEST 1: STANDARD PYTHON PRINT
    # =======================================================
    print("\n--- START TEST: PYTHON PRINT BUILD-IN ---")
    time.sleep(1)  # Pause to allow CPU to stabilize

    start_py = time.perf_counter()
    # Unpacking 10,000 arguments into the built-in print()
    print(*payload, sep="\r", file=sys.stdout)
    end_py = time.perf_counter()
    time_py = end_py - start_py

    # =======================================================
    # TEST 2: STORM FRAMEWORK PRINT (RUST)
    # =======================================================
    print("\n--- MULAI TEST: STORM LOG PRINT ---")
    time.sleep(1)

    start_rust = time.perf_counter()
    # Unpacking 10,000 arguments into Rust's FFI
    smf.printf(*payload, sep="\r", file=sys.stdout, flush=True)
    end_rust = time.perf_counter()
    time_rust = end_rust - start_rust

    # =======================================================
    # ANALYSIS RESULTS
    # =======================================================
    print("\n" + "=" * 50)
    print("🏆 BENCHMARK RESULTS (10,000 DATA)")
    print("=" * 50)
    print(f"Built-in Python : {time_py:.6f} second")
    print(f"Storm Log       : {time_rust:.6f} second")

    if time_rust < time_py:
        speedup = time_py / time_rust
        print(f"\n⚡ CONCLUSION: Your Rust Machine {speedup:.2f}x FASTER!")
    else:
        print("\nConclusion: There is a bottleneck elsewhere.")
