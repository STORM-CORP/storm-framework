RAW_NAME := signed
NAME     := libsigned.so
OUT      := $(BIN_DIR)
TARGET   := $(OUT)/$(NAME)

CACHE    := $(CARGO_TARGET_DIR)
ifeq ($(CACHE),)
    CACHE := target
endif

SRC      := $(shell find src -name "*.rs") Cargo.toml

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	@mkdir -p $(OUT)
	@cargo build --release --offline
	@cp $(CACHE)/release/lib$(RAW_NAME).so $(TARGET)
	@strip $(TARGET)

clean:
	@cargo clean
	@rm -f $(TARGET)
