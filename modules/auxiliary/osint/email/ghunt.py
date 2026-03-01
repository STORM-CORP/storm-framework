import subprocess
import json
from pathlib import Path


def call_ghunt_worker(module, target, output_name):
    # 1. Tentukan path ke Python di dalam venv GHunt
    # Sesuaikan 'script/ghunt/' dengan struktur folder aslimu
    base_path = Path(__file__).parent / "script" / "ghunt"

    # Jika Linux/Mac pakai 'bin', jika Windows pakai 'Scripts'
    python_executable = base_path / "venv" / "bin" / "python"
    worker_script = base_path / "storm_gate.py"

    # 2. Siapkan data JSON untuk dikirim
    payload = {
        "module": module,
        "target": target,
        "json_out": str(Path(__file__).parent / "results" / output_name),
    }

    try:
        # 3. Panggil prosesnya
        # Kita pakai subprocess.run karena kamu mau "Selesai -> Mati"
        process = subprocess.run(
            [str(python_executable), str(worker_script)],
            input=json.dumps(payload),  # Kirim JSON ke stdin
            text=True,
            capture_output=True,
            check=True,
        )

        return {"status": "success", "output": process.stdout}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Contoh Penggunaan:
# result = call_ghunt_worker("email", "target@gmail.com", "target_info.json")
# print(result)
