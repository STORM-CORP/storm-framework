# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from lib.smf.core.console.engine import Context

# The back command is used to exit a module that has been locked by the use command.
# because moving between modules is very flexible, back will not be used
# unless you want to see global options.
def execute(args: list[str], ctx: Context) -> None:
    
    # Checking object attributes, not key dictionary
    if ctx.current_module:
        ctx.current_module = None
        ctx.current_module_name = ""
