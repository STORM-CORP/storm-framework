import requests
import urllib3
import ssl

def storm_ssl(method, url, **kwargs):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    kwargs.setdefault('verify', False)
    kwargs.setdefault('timeout', 15)

    try:
        return requests.request(method, url, **kwargs)
    except requests.exceptions.SSLError as e:
        return f"SSL_ERROR: {e}"
    except Exception as e:
        return f"NET_ERROR: {e}"
