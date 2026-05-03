// src/tls/builder.rs
use boring::ssl::{SslContext, SslContextBuilder, SslMethod, SslOptions};
use super::{ciphers, extensions};

pub fn build_chrome_ssl_context() -> Result<SslContext, boring::error::ErrorStack> {
    // Menggunakan TLS Client method standar dari BoringSSL
    let mut builder = SslContextBuilder::new(SslMethod::tls_client())?;

    // Menghapus opsi TLS versi lama (Chrome hanya menggunakan TLS 1.2 dan 1.3)
    let mut options = SslOptions::empty();
    options.insert(SslOptions::NO_SSLV2);
    options.insert(SslOptions::NO_SSLV3);
    options.insert(SslOptions::NO_TLSV1);
    options.insert(SslOptions::NO_TLSV1_1);
    builder.set_options(options);

    // Set Cipher Suites dengan presisi Chrome
    builder.set_cipher_list(ciphers::chrome_modern_ciphers())?;
    
    // Set Curves (X25519)
    builder.set_curves_list(ciphers::chrome_curves())?;

    // Terapkan Ekstensi (GREASE & ALPN)
    extensions::apply_chrome_extensions(&mut builder)?;

    Ok(builder.build())
}
