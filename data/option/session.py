# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import lib.smf.core.sf.ldch as ldch

def default_options():
  options = {
        "IP": "",
        "PORT": "",
        "PASS": "",
        "URL": "",
        "EMAIL": "",
        "HASH": "",
        "MESSAGE": "",
        "USER": "",
        "ID": "",
        "COUNT": "",
        "PATH": "",
        "INTERFACE": "",
        "THREAD": "",
        "DOMAIN": "",
        "HOSTNAME": "",
        "MODULE": ""
    }
    options = ldch.session(options)
