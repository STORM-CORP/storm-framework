import os
import subprocess
import shutil
from rootmap import ROOT
from concurrent.futures import ProcessPoolExecutor

# Satukan semua cache di root agar tidak berantakan
SHARED_TARGET = os.path.join(ROOT, "lib", "smf", "core",  "cache", "rust_target")


def run_cmd(cmd, cwd=None):
    # Set environment variable agar Cargo tahu pakai target folder mana
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = SHARED_TARGET

    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd, env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except:
        return False

def compile_rust_project(cargo_path):
    output_dir = os.path.dirname(cargo_path)
    output_name = os.path.basename(os.path.abspath(output_dir))

    # Gunakan --offline karena kita sudah pakai cargo vendor
    # Flag --frozen memastikan Cargo tidak mengubah Cargo.lock
    cmd = "cargo build --release --quiet --offline --frozen"

    if run_cmd(cmd, cwd=output_dir):
        src_bin = os.path.join(SHARED_TARGET, "release", output_name)
        dst_bin = os.path.join(output_dir, output_name)

        if os.path.exists(src_bin):
            shutil.copy(shutil.which(src_bin) or src_bin, dst_bin)
            os.chmod(dst_bin, 0o755)
            return f"[✓] Rust: {output_name}"
    return f"[!] Rust Failed: {output_name}"

def compile_single_file(task):
    lang, src_path = task
    output = os.path.splitext(src_path)[0]

    if lang == "go":
        # Gunakan -mod=vendor jika kamu juga vendor library Go nantinya
        cmd = f"CGO_ENABLED=1 go build -o '{output}' '{src_path}'"
    else:
        with open(src_path, 'r', errors='ignore') as f:
            content = f.read()
        libs = "-lpcap" if "pcap.h" in content else ""
        cmd = f"gcc '{src_path}' -o '{output}' {libs}"

    if run_cmd(cmd):
        os.chmod(output, 0o755)
        return f"[✓] {lang.upper()}: {src_path}"
    return f"[!] {lang.upper()} Failed: {src_path}"

def main():
    os.chdir(ROOT)
    os.makedirs(SHARED_TARGET, exist_ok=True)

    rust_tasks = []
    other_tasks = []

    # SCANNING PHASE (Cepat & Akurat)
    for root, dirs, files in os.walk("."):
        # Jangan pernah masuk ke vendor atau target!
        if any(x in root for x in [".git", "vendor", "cache", "target"]):
            continue

        if "Cargo.toml" in files:
            rust_tasks.append(os.path.join(root, "Cargo.toml"))
            dirs[:] = []
            continue

        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith(".go"):
                other_tasks.append(("go", full_path))
            elif file.endswith(".c"):
                other_tasks.append(("c", full_path))

    if other_tasks and not os.path.exists("go.mod"):
        print("[*] Preparing Go Modules...")
        run_cmd("go mod init github.com/storm-os/storm-framework")
        run_cmd("go mod tidy")

    # EXECUTE PARALLEL
    print(f"[*] Storm Engine: Compiling on {os.cpu_count()} core")
    with ProcessPoolExecutor() as executor:
        # Submit Rust projects
        rust_results = list(executor.map(compile_rust_project, rust_tasks))
        # Submit Go & C files
        other_results = list(executor.map(compile_single_file, other_tasks))

    for r in rust_results + other_results: print(r)

    # FINAL CLEANUP (Hemat ruang untuk user Termux)
    # Hapus folder build_cache tapi setelah semua biner dipindah
    # shutil.rmtree(os.path.join(ROOT, "build_cache"), ignore_errors=True)

if __name__ == "__main__":
    main()
