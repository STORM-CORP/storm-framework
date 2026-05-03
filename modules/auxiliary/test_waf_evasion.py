import smf
from lib.roar.tls import get

REQUIRED_OPTIONS = {"URL": ""}


def execute(options):

    url = options.get("URL")
    try:
        cal = get(url)

        smf.printf(cal)
    except Exception as e:
        smf.printd("Exception request api openai", e, level="ERROR")
        smf.printf("ERROR EXCEPTION REQUEST API")
