# Lokasi: plugin/


def plugin(context):
    # Cek pesan dari Loader
    if context.get("event") == "startup":
        return {"auto_start": False}  # Kasih tau loader: "Jangan jalankan aku sekarang"

    if context.get("event") == "command":
        print("[+] Plugin Port Scanner berjalan...")
        # Logic penetration testing kamu di sini
