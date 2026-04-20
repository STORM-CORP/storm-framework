// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
mod core;
mod parallel;
mod writer;
mod converters;
mod errors;
mod database;
mod telemetry;

use pyo3::prelude::*;
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
    
    // 1. PENGHAPUSAN SHIM: Pengumpulan Data Native
    // args.iter() pada Bound<'_, PyTuple> secara otomatis memproduksi iterator
    // dari Bound<'_, PyAny>. Kita langsung menampungnya di memori tanpa alokasi FFI tambahan.
    let objects: Vec<Bound<'_, PyAny>> = args.iter().collect();

    // 2. Routing Logic (Deref Coercion)
    // Variabel 'objects' adalah Vec<Bound>. Saat kita mem-passing '&objects',
    // Rust secara otomatis melakukan deref coercion menjadi slice &[Bound<'_, PyAny>]
    // Parameter 'file' juga di-passing as-is tanpa mapping as_gil_ref().
    core::core_print(py, &objects, sep, end, file, flush)?;
    
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (level="DEBUG", *args))] // Default level "DEBUG", argumen objek menyusul
fn printd(
    py: Python<'_>,
    level: &str,
    args: &Bound<'_, PyTuple>,
) -> PyResult<()> {
    
    // Ubah PyTuple iterator ke array Bound secara langsung
    let objects: Vec<Bound<'_, PyAny>> = args.iter().collect();
    
    // Arahkan ke Telemetry Engine
    telemetry::execute_telemetry(py, level, &objects)?;
    
    Ok(())
}

#[pymodule]
fn smf(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(printf, m)?)?;
    m.add_function(wrap_pyfunction!(printd, m)?)?;
    Ok(())
}
