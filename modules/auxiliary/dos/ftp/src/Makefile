# --- MANDATORY CONFIG ---
# Nama binary tanpa ekstensi (Contoh: storm_scanner)
NAME     := storm_scanner

# --- PATH CONFIG ---
# BIN_DIR disuapi dari Python (Environment Variable)
OUT      := $(BIN_DIR)
TARGET   := $(OUT)/$(NAME)
# Cari semua file .go di folder ini
SOURCES  := $(wildcard *.go)

# --- RULES ---
all: $(TARGET)

$(TARGET): $(SOURCES)
	@mkdir -p $(OUT)
	@echo "[*] Building Go Binary: $(NAME)..."
	
	@# 1. Inisialisasi modul jika belum ada (Auto-fix buat user)
	@if [ ! -f go.mod ]; then \
		echo "[!] go.mod not found, initializing..."; \
		go mod init storm/$(NAME); \
	fi
	
	@# 2. Rapikan dependency (Sangat penting untuk framework besar)
	@go mod tidy
	
	@# 3. Compile tanpa simbol debug agar biner lebih kecil (Optional: -s -w)
	@go build -o $(TARGET) .
	
	@# 4. Set permission & update timestamp untuk incremental build
	@chmod +x $(TARGET)
	@touch $(TARGET)
	@echo "[✓] Go Binary created: $(TARGET)"

clean:
	rm -f $(TARGET)

