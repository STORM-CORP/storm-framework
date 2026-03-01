import subprocess
import json
from pathlib import Path
from rootmap import ROOT

REQUIRED_OPTIONS = {
    "MODULE": "",
    "PORT": "",
}


def execute(options):

    module = options.get("MODULE")
    target = options.get("EMAIL")

    output_filename = "storm-ghunt.json"
    base_path = Path(ROOT) / "script" / "ghunt"

    python_executable = base_path / "venv" / "bin" / "python"
    worker_script = base_path / "ghunt" / "ghunt.py"

    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_out_path = output_dir / output_filename

    payload = {
        "module": module,
        "target": target,
        "json_out": str(json_out_path),
    }
    try:
        process = subprocess.run(
            [str(python_executable), str(worker_script)],
            input=json.dumps(payload),  # Kirim JSON ke stdin
            text=True,
            capture_output=True,
            check=True,
        )
        return {"status": "success", "output": process.stdout}
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
