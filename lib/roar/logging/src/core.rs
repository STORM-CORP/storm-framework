// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use crate::converters::object_to_string;
use crate::writer::OutputDestination;
use crate::errors::PrintResult;

pub fn core_print(
    _py: Python<'_>,
    // 1. UBAH: Slice berisi Bound objects, bukan legacy GIL references
    objects: &[Bound<'_, PyAny>], 
    sep: &str,
    end: &str,
    // 2. UBAH: Option yang membungkus reference ke Bound object
    file: Option<&Bound<'_, PyAny>>, 
    flush: bool,
) -> PrintResult<()> {
    // 1. Inisialisasi destinasi (Stdout atau Python file object)
    // Parameter 'file' sekarang bertipe Option<&Bound<'_, PyAny>>
    let dest = OutputDestination::from_py_object(file, _py)?;
    
    // 2. Optimasi: Menulis langsung ke buffer (Streaming)
    for (idx, obj) in objects.iter().enumerate() {
        // Karena iterasi pada &[Bound<'_, PyAny>], variabel 'obj' di sini
        // otomatis bertipe &Bound<'_, PyAny>.
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
