// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use crate::converters::object_to_string;
use crate::writer::OutputDestination;
use crate::errors::PrintResult;

pub fn core_print(
    _py: Python<'_>, // Menambahkan akses ke token GIL
    objects: &[&PyAny],
    sep: &str,
    end: &str,
    file: Option<&PyAny>, // Mengikuti perubahan signature di lib.rs
    flush: bool,
) -> PrintResult<()> {
    // 1. Inisialisasi destinasi (Stdout atau Python file object)
    let mut dest = OutputDestination::from_py_object(file, _py)?;
    
    // 2. Optimasi: Menulis langsung ke buffer (Streaming)
    // Daripada membuat Vec<String> dan melakukan .join() (yang mengalokasikan memori lagi),
    // kita tulis satu per satu ke objek 'dest'.
    for (idx, obj) in objects.iter().enumerate() {
        let s = object_to_string(obj)?;
        dest.write(&s)?;
        
        // Tulis separator jika bukan elemen terakhir
        if idx < objects.len() - 1 {
            dest.write(sep)?;
        }
    }
    
    // 3. Tulis karakter penutup (end)
    dest.write(end)?;
    
    // 4. Flush jika diminta
    if flush {
        dest.flush()?;
    }
    
    Ok(())
}

