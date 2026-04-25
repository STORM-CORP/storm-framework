import importlib
import os
import smf

from apps.utility.colors import C
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.smf.core.console.engine import Context


def execute(cmd: str, args: list[str], ctx: "Context") -> bool:
    """
    Central function to search for and execute command files.
    Me-return True jika command ditemukan (terlepas dari apakah ia error atau tidak),
    dan me-return False jika command file tidak eksis.
    """
    # [Security / Sanity Check]
    # Mencegah potensi LFI / Path Traversal jika user menginputkan ".." atau slashes
    safe_cmd = os.path.basename(cmd)

    cmd_path = os.path.join("lib", "core", "commands", f"{safe_cmd}.py")

    if os.path.exists(cmd_path):
        try:
            # Import module secara dinamis
            module = importlib.import_module(f"lib.core.commands.{safe_cmd}")

            # [Eksekusi Mutasi Context]
            # Kita melempar objek `ctx` ke dalam modul command.
            # Modul tersebut akan memodifikasi properties `ctx` (seperti exit, options)
            # secara langsung di memory (in-place modification).
            module.execute(args, ctx)

            return True  # Routing berhasil di-handle

        except KeyboardInterrupt:
            # Eksekusi command dibatalkan oleh user.
            # Mengembalikan True karena command-nya *ada* dan *berjalan*, hanya saja diinterupsi.
            return True

        except Exception as e:
<<<<<<< HEAD
=======
            smf.printf(f"{C.ERROR}[-] ERROR COMMAND =>{C.RESET}", safe_cmd)
>>>>>>> origin/main
            smf.printd("ERROR WHEN EXECUTING A COMMAND", safe_cmd, e, level="CRITICAL")

            # Sama seperti KeyboardInterrupt, return True karena failure terjadi
            # di level aplikasi (runtime command), bukan di level router (command not found).
            return True

    # Me-return False murni karena file script untuk command tersebut tidak ditemukan
    return False
