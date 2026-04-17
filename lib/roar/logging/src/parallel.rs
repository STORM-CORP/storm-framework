// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use rayon::prelude::*;
use crate::converters::object_to_string;
use crate::writer::OutputDestination;
use crate::errors::PrintResult;

pub fn parallel_print(
    py: Python<'_>,
    // 1. UPDATE: Sinkron dengan lib.rs, menerima referensi Bound
    objects: &[Bound<'_, PyAny>],
    sep: &str,
    end: &str,
    // 2. UPDATE: Sinkron dengan lib.rs dan writer.rs
    file: Option<&Bound<'_, PyAny>>,
    flush: bool,
) -> PrintResult<()> {
    
    // 1. Ekstraksi Pointer (Bypass batasan Send/Sync Rayon)
    // Mengekstrak *mut ffi::PyObject lalu di-cast ke usize agar aman menyeberang thread.
    let ptrs: Vec<usize> = objects
        .iter()
        .map(|obj| obj.as_ptr() as usize)
        .collect();

    // 2. Inisialisasi Destinasi
    // 'file' sekarang diteruskan as-is (Option<&Bound>) ke writer.rs
    let dest = OutputDestination::from_py_object(file, py)?;

    // 3. Proses Paralel
    // 3. Proses Paralel (MEMPERBAIKI DEADLOCK)
    // py.allow_threads akan MELEPASKAN GIL dari thread utama saat blok ini berjalan.
    let formatted_strings: Vec<String> = py.allow_threads(|| {
        ptrs.into_par_iter()
            .map(|ptr_addr| {
                // Karena GIL sudah dilepas oleh thread utama, 
                // worker thread Rayon sekarang bisa memperebutkan/mengakuisisi GIL 
                // secara bergantian untuk memproses pointer.
                Python::with_gil(|py_inner| {
                    let ptr = ptr_addr as *mut pyo3::ffi::PyObject;
                    let bound_obj = unsafe { 
                        pyo3::Bound::<PyAny>::from_borrowed_ptr(py_inner, ptr) 
                    };

                    match object_to_string(&bound_obj) {
                        Ok(s) => s,
                        Err(_) => "ErrorRepresentation".to_string(),
                    }
                })
            })
            .collect()
    });

    // 4. Output Logic
    let mut output = formatted_strings.join(sep);
    output.push_str(end);

    dest.write(&output)?;
    if flush {
        dest.flush()?;
    }
    
    Ok(())
}
