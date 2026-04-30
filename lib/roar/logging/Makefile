.SILENT:

RAW_NAME := smf
NAME     := smf.so
OUT_DIR  ?= build
OUT      := $(OUT_ROOT)
TARGET   := $(OUT)/$(NAME)

# Cargo cache path resolution
CACHE    := $(CARGO_TARGET_DIR)
ifeq ($(CACHE),)
    CACHE := target
endif

# --- Host OS & Architecture Detection ---
OS_NAME  := $(shell uname -o 2>/dev/null || uname -s)
ARCH     := $(shell uname -m)

# --- RUSTFLAGS Base Initialization for Shared Objects ---
# 1. lto=yes              : Aggressively inline cross-crate code at the linking stage.
# 2. relocation-model=pic : Forces Position Independent Code representation (vital for .so on Android).
# 3. strip=symbols        : Delegated to LLVM instead of using the separate GNU `strip` utility.
RUST_BASE_FLAGS := -C lto=yes -C relocation-model=pic -C strip=symbols

# --- Microarchitectural Optimization Branching ---
ifeq ($(ARCH), x86_64)
    # PC/Server AMD64: Safe using native instruction sets.
    export RUSTFLAGS := $(RUST_BASE_FLAGS) -C target-cpu=native
else ifeq ($(ARCH), aarch64)
    # Mobile/ARM64: Drop target-cpu=native.
    # LLVM will fallback to generic ARM64 code-gen to ensure compatibility 
    # Application Binary Interface (ABI) across Android SoCs.
    export RUSTFLAGS := $(RUST_BASE_FLAGS)
else
    # Fallback for other architectures
    export RUSTFLAGS := $(RUST_BASE_FLAGS)
endif

SRC      := $(shell find src -name "*.rs" 2>/dev/null) Cargo.toml

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	mkdir -p $(OUT)
	# --quiet (-q) suppresses stdout/stderr logging from cargo unless a panic/abort occurs.
	cargo build --release --offline --quiet
	cp $(CACHE)/release/lib$(RAW_NAME).so $(TARGET)

clean:
	cargo clean --quiet
	rm -f $(TARGET)
