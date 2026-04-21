import smf
from lib.smfdb_helpers.log_utils import extract_logs

def execute(args, context):
    # Validasi panjang argumen. 
    # Asumsi: args adalah list kata setelah perintah utama ("take")
    if len(args) >= 2:
        cmd = args[0].lower()
        val = args[1].upper() # Contoh val: "CRITICAL", "WARN"
      
        if cmd == "log":
            # 1. Validasi Keamanan (Whitelist)
            valid_levels = {"DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"}
            if val not in valid_levels:
                smf.printf(f"[!] ERROR => Unknown log level '{val}'. Allowed: {', '.join(valid_levels)}")
                # Catat diam-diam ke SQLite bahwa user salah ketik
                smf.printd("Invalid log extraction attempt", val, level="WARN")
                return context
            
            # 2. Penamaan File Dinamis (Mencegah Overwrite)
            # Contoh hasil: "log_CRITICAL.txt"
            output_filename = f"log_{val}.txt"
            
            # 3. Eksekusi fungsi ekstraktor dengan parameter lengkap
            extract_logs(val, output_file=output_filename)
            
        else:
            # Jika user mengetik: take backup, take system, dll.
            smf.printf(f"[!] WARN => Unknown subcommand '{cmd}' for 'take'")
            
    else:
        # Jika user hanya mengetik "take" atau "take log" tanpa argumen level
        smf.printf("[!] WARN => Syntax error. Usage: take log <level>")
        # Log error sintaks ke SQLite
        smf.printd("CLI Syntax Error", args, level="DEBUG")

    return context
    
