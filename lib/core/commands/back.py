# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
#
# The back command is used to exit a module that has been locked by the use command.
# because moving between modules is very flexible, back will not be used
# unless you want to see global options.
def execute(args, context):
    if context["current_module"]:
        context["current_module"] = None
        context["current_module_name"] = ""
    return context
