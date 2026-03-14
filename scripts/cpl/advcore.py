import os

def safe_mode():
    is_android = "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux")
    total_cores = os.cpu_count() or 1
    
    if is_android:
        workers = max(1, total_cores - 2)
        print(f"[*] Linux detected > {workers}/{total_cores} cores")
    else:
        workers = total_cores
        print(f"[*] Linux Standar detected > {workers} cores")
        
    return workers
