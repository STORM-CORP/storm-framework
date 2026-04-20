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
    
    // 1. Ubah argumen objek menjadi string panjang (Butuh GIL)
    let mut messages = Vec::with_capacity(objects.len());
    for obj in objects {
        messages.push(object_to_string(obj)?);
    }
    let final_message = messages.join(" ");

    // 2. Ekstrak Waktu Universal secara Native di Rust
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs_f64();

    // 3. FFI Traceback: Pelacakan Caller (Butuh GIL)
    // Parameter call1((1,)) mengambil frame stack 1 level di atasnya.
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

    // 4. Inisialisasi Database (Butuh GIL karena memanggil rootmap)
    // Jika path tidak valid / OS menolak pembuatan folder, 
    // error akan langsung dilempar ke Python via PrintResult (?)
    let conn = get_db_connection(py)?;

    // 5. Injeksi ke Database (TANPA GIL!)
    // Perhatikan penambahan keyword `move`. Ini memerintahkan kompilator Rust 
    // untuk memindahkan kepemilikan variabel `conn` ke dalam closure secara aman.
    py.allow_threads(move || {
        // Karena ini adalah ranah log, jika disk I/O gagal (misal disk penuh), 
        // kita menggunakan `let _ =` untuk melakukan "silent fail" 
        // agar tidak membuat aplikasi utama ikut crash.
        let _ = insert_log(&conn, timestamp, level, &final_message, &caller_info);
    });

    Ok(())
}
