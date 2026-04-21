import sys
import smf


def run_sign():
    try:
        from external.source.out.core.integrity import libsigned

        libsigned.storm_sign()
        return True
    except ImportError as e:
        smf.printf(
            "[!] Critical => Binary not found.",
            file=sys.stderr,
            flush=True,
        )
        smf.printd("[!] Import error libsigned binary not found", e, level="INFO")
        return False
    except Exception as e:
        smf.printd("Error exception in libsigned", e, level="CRITICAL")
        return False


if __name__ == "__main__":
    run_sign()
