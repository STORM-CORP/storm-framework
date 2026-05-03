// src/lib.rs
mod tls;
mod http2;

use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use tokio::runtime::Runtime;

// Import modul yang sudah kita bangun
use tls::builder::build_chrome_ssl_context;
use http2::fingerprint::ChromeH2Settings;
use tokio::net::TcpStream;
use boring::ssl::Ssl;

// =========================================================================
// C-ABI / FFI BOUNDARY
// =========================================================================

#[no_mangle]
pub extern "C" fn storm_fetch(url_ptr: *const c_char) -> *mut c_char {
    // 1. Validasi Pointer dari bahasa eksternal (Python/Go)
    if url_ptr.is_null() {
        return std::ptr::null_mut();
    }

    // 2. Konversi C-String menjadi Rust String
    let c_str = unsafe { CStr::from_ptr(url_ptr) };
    let url_str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return CString::new("ERROR: Invalid UTF-8").unwrap().into_raw(),
    };

    // 3. Inisialisasi Tokio Runtime (Menjembatani kode synchronous C ke asynchronous Rust)
    let rt = match Runtime::new() {
        Ok(rt) => rt,
        Err(_) => return CString::new("ERROR: Failed to start Tokio").unwrap().into_raw(),
    };

    // 4. Eksekusi Engine secara blocking
    let result = rt.block_on(async {
        match execute_request(url_str).await {
            Ok(response_body) => response_body,
            Err(e) => format!("ERROR: Storm Engine Failure - {}", e),
        }
    });

    // 5. Konversi hasil kembali ke C-String dan serahkan memory ownership
    let c_result = CString::new(result).unwrap_or_else(|_| CString::new("ERROR: CString encoding failed").unwrap());
    c_result.into_raw()
}

#[no_mangle]
pub extern "C" fn storm_free_string(s: *mut c_char) {
    if s.is_null() {
        return;
    }
    unsafe {
        // Ambil kembali pointer, lalu Rust akan melakukan auto-drop memori
        let _ = CString::from_raw(s);
    }
}

// =========================================================================
// ASYNCHRONOUS EVASION ENGINE
// =========================================================================

/// Fungsi internal untuk menangani logika jaringan secara asynchronous
async fn execute_request(target_url: &str) -> Result<String, Box<dyn std::error::Error>> {
    // 1. Ekstraksi Host dan Port dari URL target
    let uri = target_url.parse::<http::Uri>()?;
    let host = uri.host().ok_or("URL tidak memiliki host")?;
    let port = uri.port_u16().unwrap_or(443);
    let target_addr = format!("{}:{}", host, port);

    // 2. Inisialisasi SSL Context (BoringSSL dengan Chrome Fingerprint)
    let ctx = build_chrome_ssl_context()?;
    let tcp_stream = TcpStream::connect(&target_addr).await?;
    
    let mut ssl = Ssl::new(&ctx)?;
    ssl.set_hostname(host)?; // Set SNI agar WAF tidak curiga

    // 3. TLS Handshake dengan GREASE
    let tls_stream = tokio_boring::SslStreamBuilder::new(ssl, tcp_stream)
        .connect()
        .await?;

    // 4. Negosiasi HTTP/2 dengan ALPN h2 dan Chrome H2 Settings
    let mut h2_builder = h2::client::Builder::new();
    h2_builder
        .initial_window_size(ChromeH2Settings::INITIAL_WINDOW_SIZE)
        .max_concurrent_streams(ChromeH2Settings::MAX_CONCURRENT_STREAMS)
        .header_table_size(ChromeH2Settings::HEADER_TABLE_SIZE)
        .enable_push(false);

    let (mut client, h2_connection) = h2_builder.handshake::<_, bytes::Bytes>(tls_stream).await?;

    // Pindahkan koneksi H2 ke background worker (Keep-Alive)
    tokio::spawn(async move {
        if let Err(e) = h2_connection.await {
            // Error di background, biasanya karena server menutup koneksi (GOAWAY)
            // Di production, logger akan berguna di sini.
            let _ = e;
        }
    });

    // 5. Bangun Pseudo-Headers HTTP/2
    let request = http::Request::builder()
        .method("GET")
        .uri(target_url)
        .header("host", host)
        .header("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        .header("accept", "application/json")
        .header("accept-language", "en-US,en;q=0.9")
        // Catatan: 'identity' mencegah respon dikompresi gzip/brotli agar FFI langsung bisa membaca JSON mentah
        .header("accept-encoding", "identity") 
        .body(())?;

    // 6. Kirim Request
    let (response_future, _send_stream) = client.send_request(request, true)?;
    let response = response_future.await?;

    // 7. Baca stream Response Body
    let mut body = response.into_body();
    let mut response_bytes = Vec::new();

    while let Some(chunk) = body.data().await {
        let chunk = chunk?;
        response_bytes.extend_from_slice(&chunk);
    }

    // Mengembalikan raw String ke FFI
    Ok(String::from_utf8_lossy(&response_bytes).to_string())
}
