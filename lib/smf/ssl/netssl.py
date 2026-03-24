import requests
import urllib3
import ssl


def storm_secure_call(method, url, **kwargs):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        kwargs.setdefault("verify", False)
        kwargs.setdefault("timeout", 10)

        return requests.request(method, url, **kwargs)

    except requests.exceptions.SSLError as e:
        return f"SSL_LEVEL_ERROR: {e}"
    except Exception as e:
        return f"CONN_ERROR: {e}"
