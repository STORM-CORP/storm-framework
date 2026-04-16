// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use std::io::{self, Write};
use crate::errors::{PrintError, PrintResult};

// 1. UBAH: Enum sekarang menyimpan entitas Bound pointer yang secara intrinsik 
// membawa token lifetime GIL ('py).
pub enum OutputDestination<'py> {
    Stdout,
    Stderr,
    File(Bound<'py, PyAny>),
}

impl<'py> OutputDestination<'py> {
    // 2. UBAH: Signature menerima referensi ke Bound object
    pub fn from_py_object(obj: Option<&Bound<'py, PyAny>>, _py: Python<'py>) -> PrintResult<Self> {
        match obj {
            None => Ok(OutputDestination::Stdout),
            Some(o) => {
                // Pengecekan atribut secara aman di dalam Bound context
                if o.hasattr("write")? {
                    // .clone() pada Bound tidak melakukan deep-copy data Python!
                    // Ia hanya mengeksekusi operasi C-API `Py_INCREF` (O(1) complexity) 
                    // untuk menduplikasi pointer secara aman dan menyimpannya di Enum.
                    Ok(OutputDestination::File(o.clone()))
                } else {
                    Err(PrintError::TypeError("Object lacks write method".into()))
                }
            }
        }
    }

    pub fn write(&self, data: &str) -> PrintResult<()> {
        match self {
            OutputDestination::Stdout => {
                let stdout = io::stdout();
                let mut handle = stdout.lock(); // Efisiensi: Lock manual
                handle.write_all(data.as_bytes())?;
            }
            OutputDestination::Stderr => {
                let stderr = io::stderr();
                let mut handle = stderr.lock();
                handle.write_all(data.as_bytes())?;
            }
            OutputDestination::File(obj) => {
                // 3. OPTIMASI KRITIKAL: Penghapusan Python::with_gil!
                // Kompilator Rust tahu bahwa 'obj' (Bound) hanya eksis jika GIL valid.
                // call_method1 sekarang bisa dipanggil langsung tanpa context switch FFI tambahan.
                obj.call_method1("write", (data,))?;
            }
        }
        Ok(())
    }

    pub fn flush(&self) -> PrintResult<()> {
        match self {
            OutputDestination::Stdout => io::stdout().flush()?,
            OutputDestination::Stderr => io::stderr().flush()?,
            OutputDestination::File(obj) => {
                // Penghapusan Python::with_gil
                obj.call_method0("flush")?;
            }
        }
        Ok(())
    }
}
