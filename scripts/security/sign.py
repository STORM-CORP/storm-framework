import sys


def run_sign():
    try:
        from external.source.out.core.integrity import libsigned

        libsigned.storm_sign()
        return True
    except ImportError as e:
        print(
            f"[!] Critical => Binary not found.",
            file=sys.stderr,
        )
        print(f"[!] Detail => {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[!] Runtime Error in Rust Binary => {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    run_sign()
