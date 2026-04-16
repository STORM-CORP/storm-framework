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
// Gunakan Default parameter di level Rust untuk simplifikasi
#[pyo3(signature = (*args, sep=" ", end="\n", file=None, flush=false))]
fn printf(
    py: Python<'_>,
    args: &PyTuple,
    sep: &str,
    end: &str,
    file: Option<&PyAny>,
    flush: bool,
) -> PyResult<()> {
    
    // Optimasi: Jika file None, kita bisa memilih jalur 'Raw System Call' 
    // daripada memanggil sys.stdout Python yang lambat.
    let is_stdout = file.is_none();
    
    // Ambil handle file jika ada, jika tidak, biarkan None agar ditangani modul bawah
    let file_handle = match file {
        Some(f) => Some(f),
        None => None, 
    };

    // Threshold 100 objek untuk parallel sudah masuk akal (cost vs benefit)
    if args.len() > 100 {
        // PERINGATAN: parallel_print harus menangani GIL secara internal
        parallel::parallel_print(py, args, sep, end, file_handle, flush, is_stdout)?;
    } else {
        core::core_print(py, args, sep, end, file_handle, flush, is_stdout)?;
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
    // Gunakan eprintln! agar debug info masuk ke stderr, bukan stdout
    eprintln!("[DEBUG] Objects: {}, Flush: {}", args.len(), flush);
    
    printf(py, args, sep, end, file, flush)
}

#[pymodule]
fn smf(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(printf, m)?)?;
    m.add_function(wrap_pyfunction!(printd, m)?)?;
    Ok(())
}
