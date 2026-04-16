// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use rayon::prelude::*;
use crate::converters::object_to_string;
use crate::writer::OutputDestination;
use crate::errors::PrintResult;

pub fn parallel_print(
    py: Python<'_>,
    objects: &[&PyAny],
    sep: &str,
    end: &str,
    file: Option<&PyAny>,
    flush: bool,
) -> PrintResult<()> {
    
    // 1. Ambil pointer mentah (as_ptr tidak butuh GIL di PyO3 0.21)
    let ptrs: Vec<usize> = objects
        .iter()
        .map(|obj| obj.as_ptr() as usize)
        .collect();

    // 2. Inisialisasi Destinasi
    let dest = OutputDestination::from_py_object(file, py)?;

    // 3. Proses Paralel
    let formatted_strings: Vec<String> = ptrs
        .into_par_iter()
        .map(|ptr_addr| {
            Python::with_gil(|py_inner| {
                // Menggunakan Bound API yang baru (0.21+)
                // Kita buat biner pointer kembali menjadi Bound object
                let ptr = ptr_addr as *mut pyo3::ffi::PyObject;
                
                // Gunakan unsafe secara minimal hanya untuk mengonversi pointer
                let bound_obj = unsafe { 
                    py_inner.from_borrowed_ptr::<PyAny>(ptr) 
                };

                // Panggil converter kita (pastikan object_to_string menerima &PyAny)
                // Di PyO3 0.21, Bound<PyAny> bisa di-cast ke &PyAny dengan .as_ref()
                match object_to_string(bound_obj.as_ref()) {
                    Ok(s) => s,
                    Err(_) => "ErrorRepresentation".to_string(),
                }
            })
        })
        .collect();

    // 4. Output Logic
    let mut output = formatted_strings.join(sep);
    output.push_str(end);

    dest.write(&output)?;
    if flush {
        dest.flush()?;
    }
    
    Ok(())
}
