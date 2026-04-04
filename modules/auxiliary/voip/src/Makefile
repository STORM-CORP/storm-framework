# --- Konfigurasi ---
# BIN_DIR disuapi dari Python (Environment Variable)
OUT      := $(BIN_DIR)
# Nama binary diambil dari nama folder tempat Makefile ini berada
TARGET   := $(OUT)/$(notdir $(CURDIR))
# Ambil semua file .c di folder ini
SOURCES  := $(wildcard *.c)

# --- Aturan Utama ---
all: $(TARGET)

# Hanya jalan jika file .c lebih baru daripada file binary-nya
$(TARGET): $(SOURCES)
	@mkdir -p $(OUT)
	@echo "[*] Compiling C Module: $(notdir $(CURDIR))..."
	
	@# Logika otomatis: Cek apakah butuh library pcap
	@LIBS=$$(grep -q "pcap.h" $(SOURCES) && echo "-lpcap" || echo ""); \
	gcc $(SOURCES) -o $(TARGET) $$LIBS
	
	@# Pastikan bisa dieksekusi dan update timestamp
	@chmod +55 $(TARGET)
	@touch $(TARGET)
	@echo "[✓] Output: $(TARGET)"

clean:
	rm -f $(TARGET)

