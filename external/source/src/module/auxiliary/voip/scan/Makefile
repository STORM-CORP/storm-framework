.SILENT:

NAME    := sip_scan
OUT_DIR ?= build
OUT     := $(OUT_DIR)/module/aux/voip
TARGET  := $(OUT)/$(NAME)
SRC     := $(wildcard *.go)

# --- Host OS & Architecture Detection ---
# 2>/dev/null throws stderr error if command is not supported on a particular system
OS_NAME := $(shell uname -o 2>/dev/null || uname -s)
ARCH    := $(shell uname -m)

# Variables that contain Go environment variables
GO_ENV  :=

# --- Architecture Optimization Branching ---
ifeq ($(ARCH), x86_64)
    # Optimasi khusus PC (AMD64)
    HAS_AVX512 := $(shell grep -q avx512f /proc/cpuinfo 2>/dev/null && echo "yes" || echo "no")
    HAS_AVX2   := $(shell grep -q avx2 /proc/cpuinfo 2>/dev/null && echo "yes" || echo "no")

    ifeq ($(HAS_AVX512), yes)
        GO_ENV += GOAMD64=v4
    else ifeq ($(HAS_AVX2), yes)
        GO_ENV += GOAMD64=v3
    else
        GO_ENV += GOAMD64=v2
    endif
else ifeq ($(ARCH), aarch64)
    # Bypass for ARM64 architecture (Android/Termux or Apple Silicon)
    # Ensure GOAMD64 is not triggered on ARM which could cause a fatal error
    GO_ENV += 
endif

# --- OS-Specific Adjustments ---
ifeq ($(OS_NAME), Android)
    # Disabling CGO on Android results in a pure static binary.
    # It is highly recommended that Go binaries be executable across Android devices.
    # without libc/bionic dependency issues.
    GO_ENV += CGO_ENABLED=0
endif

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	mkdir -p $(OUT)
	$(GO_ENV) go build -ldflags="-s -w" -o $(TARGET) .

clean:
	rm -rf $(OUT_DIR)
