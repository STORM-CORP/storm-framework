NAME     := dpi_netspy
OUT      := $(OUT_DIR)/module/aux/sniff
TARGET   := $(OUT)/$(NAME)
SRC      := $(wildcard *.go)

.PHONY: all clean
all: $(TARGET)

$(TARGET): $(SRC)
	@mkdir -p $(OUT)
	@go build -o $(TARGET) .

clean:
	rm -rf $(OUT)
