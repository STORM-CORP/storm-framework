// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
package main

import (
	"bufio"
	"crypto/rand"
	"crypto/tls"
	"encoding/hex"
	"flag"
	"fmt"
	"io"
	"net"
	"os"
	"strings"
	"sync"
	"time"
)

// Target struktur metadata untuk antrean pemindaian
type Target struct {
	IP       string
	Port     string
	Protocol string
}

// generateRandomHex menghasilkan string hex aman untuk parameter SIP
func generateRandomHex(n int) string {
	bytes := make([]byte, n)
	if _, err := rand.Read(bytes); err != nil {
		return "fallback-random"
	}
	return hex.EncodeToString(bytes)
}

// buildSIPOptions merakit payload RFC 3261 dinamis untuk Evasion
func buildSIPOptions(t Target, localIP string) string {
	branch := generateRandomHex(8)
	tag := generateRandomHex(6)
	callID := generateRandomHex(12)

	viaProto := strings.ToUpper(t.Protocol)

	// Payload disesuaikan agar menyerupai traffic dari IP Phone Cisco
	return fmt.Sprintf(
		"OPTIONS sip:%s:%s SIP/2.0\r\n"+
			"Via: SIP/2.0/%s %s:5060;branch=z9hG4bK%s\r\n"+
			"From: <sip:1000@%s>;tag=%s\r\n"+
			"To: <sip:1000@%s>\r\n"+
			"Call-ID: %s@%s\r\n"+
			"CSeq: 1 OPTIONS\r\n"+
			"Contact: <sip:1000@%s:5060>\r\n"+
			"Max-Forwards: 70\r\n"+
			"User-Agent: Cisco-CP-7841/11.5.1\r\n"+
			"Accept: application/sdp\r\n"+
			"Content-Length: 0\r\n\r\n",
		t.IP, t.Port, viaProto, localIP, branch, localIP, tag, t.IP, callID, localIP, localIP,
	)
}

// executeScan menangani logika layer transport per target
func executeScan(t Target, timeout time.Duration, localIP string) {
	address := net.JoinHostPort(t.IP, t.Port)
	payload := buildSIPOptions(t, localIP)

	var conn net.Conn
	var err error

	// Layer Transport Switcher
	switch t.Protocol {
	case "tls":
		conf := &tls.Config{InsecureSkipVerify: true} // Bypass validasi sertifikat
		conn, err = tls.DialWithDialer(&net.Dialer{Timeout: timeout}, "tcp", address, conf)
	case "tcp":
		conn, err = net.DialTimeout("tcp", address, timeout)
	default:
		conn, err = net.DialTimeout("udp", address, timeout)
	}

	if err != nil {
		return // Silently drop koneksi gagal untuk mengurangi noise pada stdout
	}
	defer conn.Close()

	conn.SetDeadline(time.Now().Add(timeout))
	_, err = conn.Write([]byte(payload))
	if err != nil {
		return
	}

	buffer := make([]byte, 2048)
	n, err := conn.Read(buffer)
	if err == nil && n > 0 {
		resp := string(buffer[:n])
		// Ekstrak baris pertama (Status Code) dan header Server/User-Agent jika ada
		statusLine := strings.Split(resp, "\r\n")[0]
		fmt.Printf("[+] SUCCEED | %s | %s://%s | %s\n", t.Protocol, t.Protocol, address, statusLine)
	}
}

// worker memproses antrean dari channel menggunakan rate limiter
func worker(targets <-chan Target, wg *sync.WaitGroup, timeout time.Duration, localIP string, limiter <-chan time.Time) {
	defer wg.Done()
	for t := range targets {
		if limiter != nil {
			<-limiter // Block hingga ada "tiket" dari rate limiter
		}
		executeScan(t, timeout, localIP)
	}
}

// getOutboundIP secara dinamis mencari IP lokal untuk Header SIP
func getOutboundIP() string {
	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		return "127.0.0.1"
	}
	defer conn.Close()
	localAddr := conn.LocalAddr().(*net.UDPAddr)
	return localAddr.IP.String()
}

func main() {
	// Definisi parameter fleksibel untuk Bug Hunter
	targetFlag := flag.String("t", "", "Single IP/Domain target (e.g. 192.168.1.1)")
	portFlag := flag.String("p", "5060", "Target Port (default: 5060, TLS usually 5061)")
	protoFlag := flag.String("proto", "udp", "Protocol: udp, tcp, tls")
	concurrency := flag.Int("c", 50, "Number of concurrent workers")
	timeoutMs := flag.Int("timeout", 2000, "Network timeout in milliseconds")
	rps := flag.Int("rps", 0, "Global Rate Limit (Requests Per Second). 0 = unlimited")
	flag.Parse()

	timeout := time.Duration(*timeoutMs) * time.Millisecond
	localIP := getOutboundIP()

	targets := make(chan Target, *concurrency)
	var wg sync.WaitGroup

	// Setup Global Rate Limiter (Token Bucket)
	var limiter <-chan time.Time
	if *rps > 0 {
		limiter = time.Tick(time.Second / time.Duration(*rps))
	}

	// Inisialisasi Worker Pool
	for i := 0; i < *concurrency; i++ {
		wg.Add(1)
		go worker(targets, &wg, timeout, localIP, limiter)
	}

	// Mode 1: Target Tunggal dari flag -t
	if *targetFlag != "" {
		targets <- Target{IP: *targetFlag, Port: *portFlag, Protocol: *protoFlag}
	} else {
		// Mode 2: Pipeline dari Stdin (untuk integrasi tools lain)
		stat, _ := os.Stdin.Stat()
		if (stat.Mode() & os.ModeCharDevice) == 0 {
			reader := bufio.NewReader(os.Stdin)
			for {
				line, err := reader.ReadString('\n')
				line = strings.TrimSpace(line)
				if line != "" {
					// Dukungan format IP:PORT fallback
					parts := strings.Split(line, ":")
					t := Target{Protocol: *protoFlag}
					if len(parts) >= 2 {
						t.IP = parts[0]
						t.Port = parts[1]
					} else {
						t.IP = line
						t.Port = *portFlag
					}
					targets <- t
				}
				if err == io.EOF {
					break
				}
			}
		} else {
			fmt.Fprintln(os.Stderr, "[!] No target input.")
			os.Exit(1)
		}
	}

	close(targets)
	wg.Wait()
}
