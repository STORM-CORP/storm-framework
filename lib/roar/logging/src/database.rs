// File: src/database.rs
use rusqlite::{Connection, Result as SqlResult};
use std::fs;
use std::path::Path;

pub fn get_db_connection() -> SqlResult<Connection> {
    // 1. Tentukan nama folder khusus Anda (misal: "db" atau "storage/db")
    let db_folder = "lib/sqlite/logging"; 
    let db_name = "log.db";
    
    // 2. Buat Path lengkap (db/storm_debug.sqlite)
    let folder_path = Path::new(db_folder);
    let file_path = folder_path.join(db_name);

    // 3. Logika Auto-Create Directory: Jika folder belum ada, buat sekarang.
    if !folder_path.exists() {
        // fs::create_dir_all memastikan seluruh struktur sub-folder tercipta (mkdir -p)
        let _ = fs::create_dir_all(folder_path);
    }

    // 4. Buka koneksi ke path khusus tersebut
    let conn = Connection::open(file_path)?;
    
    // Optimasi WAL tetap kita jalankan untuk performa
    conn.execute_batch(
        "PRAGMA journal_mode = WAL;
         PRAGMA synchronous = NORMAL;
         CREATE TABLE IF NOT EXISTS system_logs (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             timestamp REAL,
             level TEXT,
             message TEXT,
             caller_info TEXT
         );"
    )?;
    
    Ok(conn)
}

pub fn insert_log(
    conn: &Connection, 
    timestamp: f64, 
    level: &str, 
    message: &str, 
    caller_info: &str
) -> SqlResult<()> {
    conn.execute(
        "INSERT INTO system_logs (timestamp, level, message, caller_info) VALUES (?1, ?2, ?3, ?4)",
        (timestamp, level, message, caller_info),
    )?;
    Ok(())
}

