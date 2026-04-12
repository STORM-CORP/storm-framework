# -- https://github.com/StormWorld0/storm-framework
# -- SMF License

# Use this import when you want to use the plugin
from apps.utility.plugin.utils_plugin import plugin


# This is an example or template of how to apply the plugin
# to a logic module, feature, or whatever.
def examples():
    # Get plugin name
    func = plugin("plugin_name")

    # Get function inside plugin
    if func:
        func.plugin_function()


######
#
#
#
#
def plugin(context):
    if context.get("event") == "run":
        print("success")
