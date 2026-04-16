// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use pyo3::types::{PyString, PyBytes};
use crate::errors::{PrintError, PrintResult};

pub fn object_to_string(obj: &PyAny) -> PrintResult<String> {
    // 1. Jalur cepat: Jika sudah PyString
    if let Ok(s) = obj.downcast::<PyString>() {
        return Ok(s.to_string_lossy().into_owned());
    }
    
    // 2. Handling None (Singleton di Python)
    if obj.is_none() {
        return Ok("None".to_string());
    }

    // 3. Handling Bytes (Meniru b'...')
    if let Ok(b) = obj.downcast::<PyBytes>() {
        return Ok(format!("b'{}'", escape_bytes(b.as_bytes())));
    }
    
    // 4. Jalur Standar: Memanggil __str__ (Identik dengan print Python)
    match obj.str() {
        Ok(s) => Ok(s.to_string_lossy().into_owned()),
        Err(_) => {
            // Fallback terakhir ke repr() jika str() gagal
            match obj.repr() {
                Ok(r) => Ok(r.to_string_lossy().into_owned()),
                Err(_) => Err(PrintError::TypeError(format!(
                    "Object of type {} is not string-convertible", 
                    obj.get_type().name()?
                )))
            }
        }
    }
}

fn escape_bytes(bytes: &[u8]) -> String {
    // Pre-allocate memori untuk mengurangi re-alokasi saat string tumbuh
    let mut result = String::with_capacity(bytes.len());
    for &b in bytes {
        match b {
            b'\n' => result.push_str("\\n"),
            b'\r' => result.push_str("\\r"),
            b'\t' => result.push_str("\\t"),
            b'\\' => result.push_str("\\\\"),
            b'\'' => result.push_str("\\'"),
            // ASCII Graphic: karakter yang bisa diprint (32-126)
            0x20..=0x7E => result.push(b as char),
            _ => {
                // Format hex untuk karakter non-ASCII
                result.push_str(&format!("\\x{:02x}", b));
            }
        }
    }
    result
}

