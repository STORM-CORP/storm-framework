// src/tls/extensions.rs
use boring::ssl::SslContextBuilder;

/// Mengonfigurasi ekstensi TLS yang membuat kita terlihat seperti Chrome
pub fn apply_chrome_extensions(builder: &mut SslContextBuilder) -> Result<(), boring::error::ErrorStack> {
    // 1. Aktifkan TLS GREASE (Sangat penting untuk bypass Cloudflare)
    builder.set_grease_enabled(true);

    // 2. Set ALPN (Application-Layer Protocol Negotiation)
    // Chrome memprioritaskan HTTP/2 (h2) sebelum HTTP/1.1 (http/1.1)
    let alpn_protos = b"\x02h2\x08http/1.1";
    builder.set_alpn_protos(alpn_protos)?;

    // Catatan: Implementasi ALPS (Application-Layer Protocol Settings) murni
    // membutuhkan flag kompilasi BoringSSL spesifik yang biasanya di-patch 
    // secara manual di level C-FFI, namun GREASE + ALPN sudah cukup kuat.

    Ok(())
}
