import smf

REQUIRED_OPTIONS = {
  "IP": "",
}
def execute(options):
  smf.printd("Check options", options)
  try:
    opt = options.get("IP")
    smf.printd("Fill in the options", opt, level="INFO")
  except Exception as e:
    smf.printd("ERROR EXCEPTION", e, level="CRITICAL")
