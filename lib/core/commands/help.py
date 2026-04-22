# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import apps.base.config_ui as ui
from lib.smf.core.console.engine import Context


# Display help to make it easier for users to see what commands are available.
# Without this the user is confused about what commands are in storm.
def execute(args: list[str], ctx: Context) -> None:
    ui.show_help()
