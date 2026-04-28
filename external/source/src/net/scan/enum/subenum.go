package main

import (
	"bufio"
	"crypto/tls"
	"flag"
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// Konfigurasi HTTP Client global yang dioptimalkan
var httpClient *http.Client

func init() {
	// Custom Transport untuk bypassing dan efisiensi socket
	customTransport := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, // Wajib: abaikan cert invalid/expired
		DisableKeepAlives: true,                                  // Mencegah file descriptor exhaustion (TIME_WAIT)
		MaxIdleConns:      100,
		MaxIdleConnsPerHost: 10,
	}

	httpClient = &http.Client{
		Transport: customTransport,
		Timeout:   3 * time.Second, // Timeout agresif agar tidak hang pada server lambat
		// Mencegah client mengikuti redirect terlalu dalam secara otomatis
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 2 {
				return http.ErrUseLastResponse
			}
			return nil
		},
	}
}

// Job merepresentasikan satu task URL yang akan dieksekusi
type Job struct {
	URL string
}

// Worker function untuk memproses antrean HTTP request
func worker(jobs <-chan Job, wg *sync.WaitGroup, counter *int32) {
	defer wg.Done()
	for job := range jobs {
		// Menggunakan http.NewRequest ("HEAD") untuk meminimalisir bandwidth (tidak mendownload body HTTP)
		req, err := http.NewRequest("HEAD", job.URL, nil)
		if err != nil {
			continue
		}
		
		// Menyamarkan identitas User-Agent agar tidak diblokir proteksi dasar
		req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

		resp, err := httpClient.Do(req)
		if err != nil {
			continue // Drop request jika RTO atau DNS tidak resolve
		}
		
		// Kriteria: Berhasil jika status code < 400 atau = 403 (Forbidden sering menyembunyikan panel admin)
		if resp.StatusCode < 400 || resp.StatusCode == 403 || resp.StatusCode == 401 {
			// Format output linear agar mudah di-pipe ke bash/python
			fmt.Printf("[+] FOUND | %d | %s\n", resp.StatusCode, job.URL)
			atomic.AddInt32(counter, 1) // Operasi increment thread-safe
		}
		resp.Body.Close()
	}
}

func main() {
	// Parameter Command-Line
	domainFlag := flag.String("d", "", "Target domain (example: example.com)")
	wordlistFlag := flag.String("w", "", "Path to wordlist .txt file")
	concurrency := flag.Int("c", 100, "Number of concurrent workers")
	flag.Parse()

	if *domainFlag == "" || *wordlistFlag == "" {
		fmt.Fprintln(os.Stderr, "[!] Error: Parameters -d (domain) and -w (wordlist) are required.")
		os.Exit(1)
	}

	targetDomain := strings.TrimPrefix(strings.TrimPrefix(*domainFlag, "http://"), "https://")
	targetDomain = strings.Trim(targetDomain, "/")

	file, err := os.Open(*wordlistFlag)
	if err != nil {
		fmt.Fprintf(os.Stderr, "[!] Error opening wordlist: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	jobs := make(chan Job, *concurrency*2)
	var wg sync.WaitGroup
	var activeCount int32 = 0

	// 1. Spawning Worker Pool
	for i := 0; i < *concurrency; i++ {
		wg.Add(1)
		go worker(jobs, &wg, &activeCount)
	}

	// 2. Stream Reading file teks (O(1) Memory footprint)
	scanner := bufio.NewScanner(file)
	protocols := []string{"http", "https"}

	for scanner.Scan() {
		subdomain := strings.TrimSpace(scanner.Text())
		if subdomain == "" || strings.HasPrefix(subdomain, "#") {
			continue // Skip baris kosong atau komentar
		}

		// Injeksi job (kombinasi protokol + subdomain + domain) ke channel
		for _, proto := range protocols {
			url := fmt.Sprintf("%s://%s.%s", proto, subdomain, targetDomain)
			jobs <- Job{URL: url}
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "[!] Error while reading wordlist: %v\n", err)
	}

	// 3. Cleanup: Tutup channel dan tunggu goroutines selesai
	close(jobs)
	wg.Wait()

	// Cetak rangkuman ke stderr agar tidak tercampur dengan hasil stdout jika di-pipe
	fmt.Fprintf(os.Stderr, "\n[*] Enumeration complete. Found %d active subdomain.\n", atomic.LoadInt32(&activeCount))
}

