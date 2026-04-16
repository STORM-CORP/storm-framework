// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
mod core;
mod parallel;
mod writer;
mod converters;
mod errors;

use pyo3::prelude::*;
use pyo3::types::PyTuple;

#[pyfunction]
#[pyo3(signature = (*args, sep=" ", end="\n", file=None, flush=false))]
fn printf(
    py: Python<'_>,
    args: &PyTuple,
    sep: &str,
    end: &str,
    file: Option<&PyAny>,
    flush: bool,
) -> PyResult<()> {
    // 1. Konversi PyTuple ke Vec<&PyAny> (SANGAT PENTING)
    let objects: Vec<&PyAny> = args.iter().collect();
    
    // 2. Thresholding
    // Gunakan objects.len() karena args adalah PyTuple
    if objects.len() > 100 {
        // PERBAIKAN: Sesuaikan dengan signature parallel_print (6 argumen)
        // Hapus 'args' dan 'is_stdout' karena info is_stdout sudah ada di dalam logic file.is_none()
        parallel::parallel_print(py, &objects, sep, end, file, flush)?;
    } else {
        // PERBAIKAN: Sesuaikan dengan signature core_print (6 argumen)
        core::core_print(py, &objects, sep, end, file, flush)?;
    }
    
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (*args, sep=" ", end="\n", file=None, flush=false))]
fn printd(
    py: Python<'_>,
    args: &PyTuple,
    sep: &str,
    end: &str,
    file: Option<&PyAny>,
    flush: bool,
) -> PyResult<()> {
    // Menulis ke stderr secara langsung di Rust (Instant Debug)
    eprintln!("[DEBUG] Printing {} objects via smf.printd", args.len());
    
    // Delegasikan ke printf
    printf(py, args, sep, end, file, flush)
}

#[pymodule]
fn smf(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(printf, m)?)?;
    m.add_function(wrap_pyfunction!(printd, m)?)?;
    Ok(())
}
