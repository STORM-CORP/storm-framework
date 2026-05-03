// src/http2/fingerprint.rs

/// Konstanta HTTP/2 SETTINGS Frame untuk meniru Chrome
pub struct ChromeH2Settings;

impl ChromeH2Settings {
    // Chrome biasanya menetapkan concurrent streams ke 1000
    pub const MAX_CONCURRENT_STREAMS: u32 = 1000;
    
    // Initial window size milik Chrome (biasanya lebih besar dari standar)
    pub const INITIAL_WINDOW_SIZE: u32 = 6291456; 
    
    // Header table size spesifik
    pub const HEADER_TABLE_SIZE: u32 = 65536;

    /// Urutan pseudo-header yang wajib dipatuhi untuk bypass Akamai
    pub fn get_pseudo_header_order() -> Vec<&'static str> {
        vec![
            ":method",
            ":authority",
            ":scheme",
            ":path",
        ]
    }
}
