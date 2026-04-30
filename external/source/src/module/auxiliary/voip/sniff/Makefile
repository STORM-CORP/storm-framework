.SILENT:

NAME     := rtp_sniff
OUT_DIR  ?= build
OUT      := $(OUT_DIR)/module/aux/voip
TARGET   := $(OUT)/$(NAME)
SOURCES  := $(wildcard *.c)

# --- Operating System Detection (Not CPU) ---
UNAME_O := $(shell uname -o 2>/dev/null || echo "Unknown")

# --- Toolchain Initialization & Hardware Optimization ---
CC      ?= gcc
# Compile-on-Device Paradigm: 
# -march=native -mtune=native is installed universally. GCC/Clang will 
# squeeze 100% of specific instructions from the local CPU without regard 
# whether it is x86_64 PC processor or aarch64 HP.
CFLAGS  := -O3 -pipe -march=native -mtune=native
LDFLAGS :=

# --- OS-Specific Memory Compliance ---
ifeq ($(UNAME_O),Android)
    # Modern Termux/Android is based on LLVM, clang is recommended.
    CC      := clang
    # Position Independent Code Injection is mandatory for the Android kernel
    CFLAGS  += -fPIE -fPIC
    LDFLAGS += -pie
endif

# --- Dynamic Dependency Resolution ---
HAS_PCAP := $(shell grep -q "pcap.h" $(SOURCES) 2>/dev/null && echo 1 || echo 0)
ifeq ($(HAS_PCAP),1)
    LDFLAGS += -lpcap
endif

# --- Build Rules ---
.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	mkdir -p $(OUT)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET) $(LDFLAGS)
	strip --strip-unneeded $(TARGET) 2>/dev/null || true

clean:
	rm -f $(TARGET)
