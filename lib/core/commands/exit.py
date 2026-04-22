# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from lib.smf.core.console.engine import Context


# Exit command to avoid errors or crashes in storm.
# Because if you only use CTRL + C it is possible that the storm will come out messy.
# This will minimize the possibility of a crash to prevent damage.
def execute(args: list[str], ctx: Context) -> None:
    # Mutate state exit in-place
    ctx.exit = True
