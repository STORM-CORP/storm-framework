NAME     := smtp_flood
OUT      := $(OUT_DIR)/mod/aux/dos/smtp
TARGET   := $(OUT)/$(NAME)
SRC      := $(wildcard *.go)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	@mkdir -p $(OUT)
	@go build -o $(TARGET) .

clean:
	rm -rf $(OUT)
