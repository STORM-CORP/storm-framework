import dns.resolver
import dns.exception
import socket
import ipaddress
from apps.utility.colors import C

MOD_INFO = {
    "Name": "Scanning DNS Records",
    "Description": """
Scan the DNS Record to find out the DNS data in it
used by a website.
""",
    "Author": ["zxelzy"],
    "Action": [
        ["Scanner", {"Description": "Scan DNS Records"}],
    ],
    "DefaultAction": "Scanner",
    "License": "SMF License",
}
SYM_INFO = "💡"
SYM_SECURITY = "🔒"
DNS_RECORDS = [
    # === Core addressing ===
    "A",  # IPv4
    "AAAA",  # IPv6
    "CNAME",  # Alias / takeover risk
    # === Mail ===
    "MX",  # Mail server
    "TXT",  # SPF, DKIM, DMARC, verification
    # === Authority & zone ===
    "NS",  # Nameserver
    "SOA",  # Zone info (serial, refresh)
    # === Service discovery ===
    "SRV",  # _sip, _ldap, _xmpp, internal services
    "NAPTR",  # VoIP / telecom
    # === Security / SSL ===
    "CAA",  # Allowed CA (fingerprinting infra)
    "TLSA",  # DANE
    # === Reverse / legacy ===
    "PTR",
    # === DNSSEC (info only)
    "DNSKEY",
    "DS",
    "RRSIG",
    # === Microsoft / enterprise vibes ===
    "LOC",
]

REQUIRED_OPTIONS = {"DOMAIN": ""}


def execute(options):
    target_domain = options.get("DOMAIN")
    if not target_domain:
        return

    try:
        ipaddress.ip_address(target_domain)
        return
    except ValueError:
        pass

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
    resolver.timeout = 2.0
    resolver.lifetime = 3.0

    print(f"{C.HEADER} DNS ENUMERATION For {target_domain}")
    try:
        socket.gethostbyname(target_domain)
        for record_type in DNS_RECORDS:
            try:
                answers = resolver.resolve(target_domain, record_type)
                print(f"{C.MENU} \n[{record_type} Records]:")
                for rdata in answers:
                    if record_type == "TXT":
                        print(f"{C.SUCCESS}  {SYM_SECURITY} {rdata}")
                    else:
                        print(f"{C.MENU}  {SYM_INFO} {rdata}")

            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                continue
            except dns.exception.Timeout:
                print(f"{C.ERROR}[!] Timeout: {record_type}")
            except Exception as e:
                print(f"{C.ERROR}[!] ERROR {record_type}: {e}")

    except socket.gaierror:
        print(f"{C.ERROR}[!] ERROR: Domain not found.")
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"{C.ERROR}[!] Global ERROR: {e}")
