import os


def safe_mode():
    term = "TERMUX_VERSION" in os.environ
    total_cores = os.cpu_count() or 1

    if term:
        workers = max(1, total_cores - 2)
        print(f"[*] Linux detected > {total_cores} cores")
    else:
        workers = total_cores
        print(f"[*] Linux Standar detected > {workers} cores")

    return workers
