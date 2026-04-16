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

    // Konversi slice menjadi Vec agar Rayon bisa memanggil into_par_iter() dengan pasti
    let obj_vec: Vec<&PyAny> = objects.to_vec();

    // Inisialisasi Destinasi (Stdout atau Python File)
    let dest = OutputDestination::from_py_object(file, py)?;

    // Gunakan Rayon untuk pemrosesan paralel yang aman
    // Kita kumpulkan ke Vec<String> agar urutan tetap terjaga sesuai index asli
    let formatted_strings: Vec<String> = obj_vec
        .into_par_iter() // Sekarang ini akan bekerja karena Vec memuaskan trait bounds
        .map(|obj| {
            Python::with_gil(|py_inner| {
                // Gunakan .bind(py) karena kita di PyO3 0.21
                match object_to_string(obj) {
                    Ok(s) => s,
                    Err(_) => "ErrorRepresentation".to_string(),
                }
            })
        })
        .collect(); // Rayon menjamin urutan hasil collect sesuai urutan input

    // Join strings di thread utama
    let mut output = formatted_strings.join(sep);
    output.push_str(end);

    // I/O Operation (Serial)
    dest.write(&output)?;
    
    if flush {
        dest.flush()?;
    }
    
    Ok(())
}

