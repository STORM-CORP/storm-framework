// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
mod core;
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
    
    // Konversi tuple iterator ke Vec<Bound> dengan alokasi O(1)
    let objects: Vec<Bound<'_, PyAny>> = args.iter().collect();

    // Routing ke memori sekuensial (Fast-path)
    // PrintResult otomatis dikonversi menjadi PyResult (PyErr) berkat implementasi From di errors.rs
    core::core_print(py, &objects, sep, end, file, flush)?;
    
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (*args, level="DEBUG"))] 
fn printd(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    level: &str,
) -> PyResult<()> {
    
    // Ekstraksi seluruh pesan pengguna tanpa terpotong
    let objects: Vec<Bound<'_, PyAny>> = args.iter().collect();
    
    // Arahkan ke Telemetry Engine
    // Sama seperti printf, error internal (seperti SQLite error/IO error) 
    // akan terlempar otomatis ke Python jika terjadi kegagalan fatal.
    telemetry::execute_telemetry(py, level, &objects)?;
    
    Ok(())
}

#[pymodule]
fn smf(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(printf, m)?)?;
    m.add_function(wrap_pyfunction!(printd, m)?)?;
    Ok(())
}
