def run_sign():
    try:
        from external.source.binary import signed

        signed()
        return True
    except ImportError as e:
        print(f"[!] Critical: Binary 'storm_sign' not found or ABI mismatch.", file=sys.stderr)
        print(f"[!] Detail => {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[!] Runtime Error in Rust Binary => {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    run_sign()
