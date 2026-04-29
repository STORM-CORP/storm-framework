// GPL License.
// Copyright (c) 2026 Storm Framework
// See LICENSE file in the project root for full license information.
#include <pcap.h>
#include <stdio.h>
#include <stdlib.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
FILE *pcm_file;
void packet_handler(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    // Offset: Ethernet(14) + IP(20) + UDP(8) = 42 bytes
    // RTP Header: 12 bytes
    const u_char *rtp_payload = packet + 42 + 12;
    int payload_size = header->len - (42 + 12);
    if (payload_size > 0) {
        fwrite(rtp_payload, 1, payload_size, pcm_file);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <interface> <output_path>\n", argv[0]);
        return 1;
    }

    char *dev = argv[1];
    char *out_path = argv[2];
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle;

    pcm_file = fopen(out_path, "wb");
    if (!pcm_file) {
        perror("[!] Error opening output file");
        return 1;
    }

    handle = pcap_open_live(dev, BUFSIZ, 1, 1000, errbuf);
    if (!handle) {
        fprintf(stderr, "[!] Could not open device %s: %s\n", dev, errbuf);
        return 2;
    }

    struct bpf_program fp;
    if (pcap_compile(handle, &fp, "udp portrange 10000-20000", 0, PCAP_NETMASK_UNKNOWN) == -1) {
        fprintf(stderr, "[!] Bad filter\n");
        return 3;
    }
    pcap_setfilter(handle, &fp);

    printf("[*] Engine: Captured packets writing to %s\n", out_path);
    pcap_loop(handle, 0, packet_handler, NULL);

    fclose(pcm_file);
    pcap_close(handle);
    return 0;
}
