NAME     := rtp_sniff
OUT      := $(OUT_DIR)/mod/aux/voip
TARGET   := $(OUT)/$(NAME)
SOURCES  := $(wildcard *.c)

.PHONY: all clean
all: $(TARGET)

$(TARGET): $(SOURCES)
	@mkdir -p $(OUT)
	@LIBS=$$(grep -q "pcap.h" $(SOURCES) && echo "-lpcap" || echo ""); \
	gcc $(SOURCES) -o $(TARGET) $$LIBS

clean:
	rm -f $(TARGET)

