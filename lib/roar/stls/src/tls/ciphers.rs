// src/tls/ciphers.rs

/// Mengembalikan representasi string cipher suites modern Chrome
/// Urutan ini sangat krusial untuk JA3 Fingerprint.
pub fn chrome_modern_ciphers() -> &'static str {
    // Kombinasi TLS 1.3 dan TLS 1.2 fallback sesuai urutan Chrome
    concat!(
        "TLS_AES_128_GCM_SHA256:",
        "TLS_AES_256_GCM_SHA384:",
        "TLS_CHACHA20_POLY1305_SHA256:",
        "ECDHE-ECDSA-AES128-GCM-SHA256:",
        "ECDHE-RSA-AES128-GCM-SHA256:",
        "ECDHE-ECDSA-AES256-GCM-SHA384:",
        "ECDHE-RSA-AES256-GCM-SHA384:",
        "ECDHE-ECDSA-CHACHA20-POLY1305:",
        "ECDHE-RSA-CHACHA20-POLY1305"
    )
}

/// Curve Elliptic (termasuk X25519)
pub fn chrome_curves() -> &'static str {
    // Memprioritaskan X25519 (Chrome default) 
    "X25519:P-256:P-384"
}
