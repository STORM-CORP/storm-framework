// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use rayon::prelude::*;
use crate::converters::object_to_string;
use crate::writer::OutputDestination;
use crate::errors::PrintResult;

pub fn parallel_print(
    py: Python<'_>, // Butuh py untuk safety
    objects: &[&PyAny],
    sep: &str,
    end: &str,
    file: Option<&PyAny>,
    flush: bool,
) -> PrintResult<()> {
    
    // 1. Inisialisasi Destinasi (Stdout atau Python File)
    let dest = OutputDestination::from_py_object(file, py)?;

    // 2. Gunakan Rayon untuk pemrosesan paralel yang aman
    // Kita kumpulkan ke Vec<String> agar urutan tetap terjaga sesuai index asli
    let formatted_strings: Vec<String> = objects
        .par_iter() // Gunakan .par_iter() bukan .into_par_iter() untuk slice
        .map(|obj| {
            Python::with_gil(|py| {
                // Gunakan .bind(py) karena kita di PyO3 0.21
                match object_to_string(obj) {
                    Ok(s) => s,
                    Err(_) => "ErrorRepresentation".to_string(),
                }
            })
        })
        .collect(); // Rayon menjamin urutan hasil collect sesuai urutan input

    // 3. Join strings di thread utama
    let output = formatted_strings.join(sep) + end;

    // 4. I/O Operation (Serial)
    dest.write(&output)?;
    
    if flush {
        dest.flush()?;
    }
    
    Ok(())
}

