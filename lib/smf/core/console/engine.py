# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import typing
import smf
import data.option.session as ops

from lib.core import handler as ex
from lib.roar.plugin_api import plugin
from dataclasses import dataclass, field


@dataclass
class Context:
    """
    A representation of the Framework's execution state.
    This context is what the Pipeline will carry everywhere.
    """

    current_module: typing.Any = None
    current_module_name: str = ""
    options: dict = field(default_factory=ops.default_options)
    exit: bool = False

    # Put core plugin into context
    plugin: typing.Any = plugin

    smf.printd("CONTEXT CURRENT MODULE", current_module, level="DEBUG")
    smf.printd("CONTEXT CURRENT MODULE NAME", current_module_name, level="DEBUG")
    smf.printd("CONTEXT OPTIONS", options, level="DEBUG")
    smf.printd("CONTEXT EXIT", exit, level="DEBUG")
    smf.printd("CONTEXT PLUGIN", plugin, level="DEBUG")

    def dispatch(self, cmd: str, args: list[str]) -> None:
        """
        This method is the gateway to the handler.
        Pipeline: Input -> Core (self) -> Handler -> Commands
        """
        # Pass 'self' (this context object itself) to the handler.
        # ex.execute now does not need to return a new dict,
        handled = ex.execute(cmd, args, self)

        # Log all to internal
        smf.printd("Capture cmd dispatch", cmd, level="DEBUG")
        smf.printd("Capture dispatch args", args, level="DEBUG")
        smf.printd("Capturing self from context", self, level="DEBUG")

        if not handled:
            smf.printf(
                f"[-] Unknown Command => {cmd} > Run the <help> command for more details."
            )
