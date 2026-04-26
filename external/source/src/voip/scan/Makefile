NAME     := sip_scan
OUT      := $(OUT_DIR)/voip
TARGET   := $(OUT)/$(NAME)
SRC      := $(wildcard *.go)

.PHONY: all clean
all: $(TARGET)

$(TARGET): $(SRC)
    @mkdir -p $(OUT)
    @go build -o $(TARGET) .

clean:
    rm -rf $(OUT)
