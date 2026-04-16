// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
mod core;
mod parallel;
mod writer;
mod converters;
mod errors;

use pyo3::prelude::*;
// Import PyModule dan PyTuple langsung agar kode lebih bersih
use pyo3::types::{PyModule, PyTuple};

#[pyfunction]
#[pyo3(signature = (*args, sep=" ", end="\n", file=None, flush=false))]
fn printf(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    sep: &str,
    end: &str,
    file: Option<&Bound<'_, PyAny>>,
    flush: bool,
) -> PyResult<()> {
    
    // 1. Konversi Iterator: Bound<'_, PyAny> -> &PyAny
    // Menggunakan .into_gil_ref() untuk downcast ke tipe lama secara aman
    let objects: Vec<&PyAny> = args
        .iter()
        .map(|bound_item| bound_item.into_gil_ref())
        .collect();
    
    // 2. Mapping Option file: Option<&Bound> -> Option<&PyAny>
    let legacy_file: Option<&PyAny> = file.map(|b| b.as_gil_ref());

    // 3. Routing Logic
    if objects.len() > 100 {
        parallel::parallel_print(py, &objects, sep, end, legacy_file, flush)?;
    } else {
        core::core_print(py, &objects, sep, end, legacy_file, flush)?;
    }
    
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (*args, sep=" ", end="\n", file=None, flush=false))]
fn printd(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    sep: &str,
    end: &str,
    file: Option<&Bound<'_, PyAny>>,
    flush: bool,
) -> PyResult<()> {
    eprintln!("[DEBUG] Printing {} objects via smf.printd", args.len());
    
    // Delegasikan secara transparan
    printf(py, args, sep, end, file, flush)
}

// 4. Perbaikan inisialisasi modul (Pure Bound API)
#[pymodule]
fn smf(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(printf, m)?)?;
    m.add_function(wrap_pyfunction!(printd, m)?)?;
    Ok(())
}
