// File: src/telemetry.rs
use pyo3::prelude::*;
use std::time::{SystemTime, UNIX_EPOCH};
use crate::converters::object_to_string;
use crate::database::{get_db_connection, insert_log};
use crate::errors::PrintResult;

pub fn execute_telemetry(
    py: Python<'_>,
    level: &str,
    objects: &[Bound<'_, PyAny>],
) -> PrintResult<()> {
    
    // 1. Ubah argumen objek menjadi string panjang
    let mut messages = Vec::with_capacity(objects.len());
    for obj in objects {
        messages.push(object_to_string(obj)?);
    }
    let final_message = messages.join(" ");

    // 2. Ekstrak Waktu Universal (Milidetik) secara Native di Rust
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs_f64();

    // 3. FFI Black Magic: Melacak Traceback (Caller)
    // Kita panggil sys._getframe(1) milik Python untuk tahu persis 
    // siapa yang memanggil fungsi printd ini.
    let caller_info = match py.import_bound("sys").and_then(|sys| sys.getattr("_getframe")) {
        Ok(getframe) => {
            if let Ok(frame) = getframe.call1((1,)) {
                let filename = frame.getattr("f_code").and_then(|c| c.getattr("co_filename"));
                let lineno = frame.getattr("f_lineno");
                
                if let (Ok(f), Ok(l)) = (filename, lineno) {
                    format!("{}:{}", f.to_string_lossy(), l.extract::<usize>().unwrap_or(0))
                } else {
                    "UnknownLocation".to_string()
                }
            } else {
                "UnknownFrame".to_string()
            }
        },
        Err(_) => "SysModuleError".to_string(),
    };

    // 4. Injeksi ke Database (TANPA GIL!)
    // Kita lepaskan GIL agar tidak membuat aplikasi Python lag saat Rust 
    // menulis data ke hard disk.
    py.allow_threads(|| {
        if let Ok(conn) = get_db_connection() {
            let _ = insert_log(&conn, timestamp, level, &final_message, &caller_info);
        }
    });

    Ok(())
}

