// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use std::io::{self, Write};
use crate::errors::{PrintError, PrintResult};

pub enum OutputDestination<'py> {
    Stdout,
    Stderr,
    File(&'py PyAny),
}

impl<'py> OutputDestination<'py> {
    // Menambahkan parameter 'py' untuk konsistensi dengan lib.rs
    pub fn from_py_object(obj: Option<&'py PyAny>, _py: Python<'py>) -> PrintResult<Self> {
        match obj {
            None => Ok(OutputDestination::Stdout),
            Some(o) => {
                if o.hasattr("write")? {
                    Ok(OutputDestination::File(o))
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
                // JANGAN flush di sini agar buffering bekerja
            }
            OutputDestination::Stderr => {
                let stderr = io::stderr();
                let mut handle = stderr.lock();
                handle.write_all(data.as_bytes())?;
            }
            OutputDestination::File(obj) => {
                // Memanggil method Python tetap butuh GIL
                Python::with_gil(|_py| {
                    obj.call_method1("write", (data,))?;
                    Ok::<(), PyErr>(())
                })?;
            }
        }
        Ok(())
    }

    pub fn flush(&self) -> PrintResult<()> {
        match self {
            OutputDestination::Stdout => io::stdout().flush()?,
            OutputDestination::Stderr => io::stderr().flush()?,
            OutputDestination::File(obj) => {
                Python::with_gil(|_py| {
                    obj.call_method0("flush")?;
                    Ok::<(), PyErr>(())
                })?;
            }
        }
        Ok(())
    }
}

