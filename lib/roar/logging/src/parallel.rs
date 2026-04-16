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
    
    // 1. Ambil pointer mentah dari objek agar Rayon tidak protes soal thread-safety
    // Kita simpan sebagai usize (alamat memori)
    let ptrs: Vec<usize> = objects
        .iter()
        .map(|obj| obj.as_ptr() as usize)
        .collect();

    // 2. Inisialisasi Destinasi
    let dest = OutputDestination::from_py_object(file, py)?;

    // 3. Proses Paralel menggunakan Pointer
    let formatted_strings: Vec<String> = ptrs
        .into_par_iter()
        .map(|ptr_addr| {
            Python::with_gil(|py_inner| {
                // Kembalikan pointer mentah menjadi objek PyAny yang valid
                unsafe {
                    let obj = py_inner.from_owned_ptr_or_err(ptr_addr as *mut pyo3::ffi::PyObject)
                        .unwrap_or_else(|_| py_inner.None().into_bound());
                    
                    // Gunakan fungsi konversi kita (pastikan kompatibel dengan Bound API atau as_ref)
                    match object_to_string(obj.as_ref()) {
                        Ok(s) => s,
                        Err(_) => "ErrorRepresentation".to_string(),
                    }
                }
            })
        })
        .collect();

    // 4. Join dan Write
    let mut output = formatted_strings.join(sep);
    output.push_str(end);

    dest.write(&output)?;
    if flush {
        dest.flush()?;
    }
    
    Ok(())
}
