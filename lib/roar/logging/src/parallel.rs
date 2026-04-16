// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use rayon::prelude::*;
use crate::converters::object_to_string;
use crate::writer::OutputDestination;
use crate::errors::PrintResult;

pub fn parallel_print(
    py: Python<'_>,
    // Catatan: Jika memungkinkan, update signature eksternal ini menjadi &[Bound<'_, PyAny>] ke depannya.
    objects: &[&PyAny], 
    sep: &str,
    end: &str,
    file: Option<&PyAny>,
    flush: bool,
) -> PrintResult<()> {
    
    // 1. Ambil pointer mentah
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
                let ptr = ptr_addr as *mut pyo3::ffi::PyObject;
                
                // Menggunakan Bound API yang direkomendasikan di PyO3 0.21+
                let bound_obj = unsafe { 
                    pyo3::Bound::<PyAny>::from_borrowed_ptr(py_inner, ptr) 
                };

                // JIKA object_to_string sudah menerima `&Bound<'_, PyAny>`:
                // match object_to_string(&bound_obj) {
                
                // JIKA object_to_string MASIH menerima `&PyAny` (Legacy):
                // Gunakan .as_gil_ref() sebagai jembatan sementara antar API
                match object_to_string(bound_obj.as_gil_ref()) {
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
