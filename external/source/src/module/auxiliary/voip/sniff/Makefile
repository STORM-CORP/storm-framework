.SILENT:

NAME     := rtp_sniff
OUT_DIR  ?= build
OUT      := $(OUT_DIR)/module/aux/voip
TARGET   := $(OUT)/$(NAME)
SOURCES  := $(wildcard *.c)

# --- Host Detection ---
UNAME_S := $(shell uname -s)
UNAME_O := $(shell uname -o 2>/dev/null || echo "Unknown")

# --- Toolchain Initialization & Base Flags ---
CC      ?= gcc
CFLAGS  := -O3 -pipe
LDFLAGS :=

# --- Environment Branching Logic ---
ifeq ($(UNAME_O),Android)
    # --- Android Configuration (Termux / Native) ---
    CC      := clang
    CFLAGS  += -fPIE -fPIC
    LDFLAGS += -pie

else ifeq ($(UNAME_S),Linux)
    # --- GNU/Linux Configuration (PC) ---
    CFLAGS  += -march=native -mtune=native

else ifeq ($(UNAME_S),Darwin)
    # --- macOS Configuration ---
    CC      := clang
    CFLAGS  += -march=native -mtune=native

else
    # --- Fallback (Windows MSYS2, Cygwin, etc) ---
    CFLAGS  += -march=native -mtune=native
endif

# --- Dynamic Dependency Resolution ---
# Added 2>/dev/null to grep to prevent stderr leaking if $(SOURCES) is empty.
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

clean:
	rm -f $(TARGET)
