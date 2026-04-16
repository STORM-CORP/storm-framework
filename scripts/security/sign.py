import sys
import smf


def run_sign():
    try:
        from external.source.out.core.integrity import libsigned

        libsigned.storm_sign()
        return True
    except ImportError as e:
        smf.printf(
            f"[!] Critical => Binary not found.",
            file=sys.stderr,
            flush=True,
        )
        smf.printf(f"[!] Detail =>", e, file=sys.stderr, flush=True)
        return False
    except Exception as e:
        smf.printf(
            f"[!] Runtime Error in Rust Binary =>", e, file=sys.stderr, flush=True
        )
        return False


if __name__ == "__main__":
    run_sign()
