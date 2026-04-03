import app.base.config_ui as ui

# -- https://github.com/StormWorld0/storm-framework/app/base/config_ui
#
# The about command is used to display developer information, etc.
# to find out who the creator, contributor, version, etc.
# This is useful for very specific information.
def execute(args, context):
    ui.show_about()
    return context
