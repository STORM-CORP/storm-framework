// File: src/database.rs
use rusqlite::{Connection, Result as SqlResult};
use std::path::Path;

pub fn get_db_connection() -> SqlResult<Connection> {
    // Menyimpan log internal di folder tempat script dijalankan
    let db_path = Path::new("storm_internal_debug.sqlite");
    
    let conn = Connection::open(db_path)?;
    
    // Optimasi mutakhir untuk logging kecepatan tinggi
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

