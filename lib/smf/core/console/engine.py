# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import typing
import smf
import data.option.session as ops

from apps.utility.colors import *
from lib.core import handler as ex
from lib.roar.plugin import app
from dataclasses import dataclass, field


@dataclass
class Context:
    """
    Representasi dari State Eksekusi Framework.
    Context ini yang akan dibawa kemana-mana oleh Pipeline.
    """

    current_module: typing.Any = None
    current_module_name: str = ""
    options: dict = field(default_factory=ops.default_options)
    exit: bool = False

    # Put core plugin into context
    plugin: typing.Any = app

    def dispatch(self, cmd: str, args: list[str]) -> None:
        """
        Method ini adalah Pintu Masuk ke Handler.
        Pipeline: Input -> Core (self) -> Handler -> Commands
        """
        # Melempar 'self' (objek context ini sendiri) ke handler.
        # ex.execute sekarang tidak perlu mereturn dict baru,
        # cukup modifikasi atribut objek context ini secara in-place.
        handled = ex.execute(cmd, args, self)

        if not handled:
            # Pindahkan logika error handling unknown command ke sini
            # agar main.py benar-benar bersih dari logika bisnis.
            smf.printf(
                f"[-] Unknown Command => {cmd} > Run the {CC.SUCCESS}help{CC.RESET} command for more details."
            )
